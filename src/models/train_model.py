from torch.utils.data.dataset import Dataset
import random
import numpy as np
import os
import torch
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel, DataCollatorWithPadding, Trainer, TrainingArguments

class TokenSequenceDataset(Dataset):

    def __init__(self, tokenizer, dataset_paths, block_size, simulate=False):

        pad_token_id = tokenizer.encode("[PAD]")[0]
        unk_token_id = tokenizer.encode("[UNK]")[0]

        # Read all lines from all files.
        lines = []
        for dataset_path in dataset_paths:
            assert os.path.isfile(dataset_path), f"Input file path {dataset_path} not found"
            lines += open(dataset_path, "r").readlines()

        # In simulation just use a few samples.
        if simulate:
            random.shuffle(lines)
            lines = lines[:10]

        # Turn lines into training examples. Also gather some statistics.
        self.examples = []
        unknown_tokens_set = []
        unknown_tokens = []
        tokens_count = 0
        unknown_token_lines_count = 0
        too_long_lines_count = 0
        encoded_lengths = []
        for line in lines:

            #Skip empty lines.
            line = line.strip()
            if line == "":
                continue

            # Encode the line.
            encoded_line = tokenizer.encode(line)
            encoded_lengths += [len(encoded_line)]
            tokens_count += len(encoded_line)

            # Create a warning about unknown tokens. And then skip the line.
            if unk_token_id in encoded_line:
                index = encoded_line.index(unk_token_id)
                token = tokenizer.decode(encoded_line[index])
                token = line.split()[index]
                if token not in unknown_tokens_set:
                    unknown_tokens_set += [token]
                #logger.warning(f"Skipping line because of unknown token {token}")
                unknown_tokens += [token]
                unknown_token_lines_count += 1
                continue

            # Skip sequence if it is too long.
            if len(encoded_line) > block_size:
                #logger.warning(f"Skipping line because it is too long... {len(encoded_line)} > {block_size}")
                too_long_lines_count += 1
                continue

            # Pad and truncate.
            tensor = np.full((block_size,), pad_token_id, dtype=np.longlong)
            tensor[:len(encoded_line)] = encoded_line
            assert len(tensor) == block_size

            self.examples += [{
                "input_ids": torch.tensor(tensor, dtype=torch.long),
                "labels": torch.tensor(tensor, dtype=torch.long)
            }]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return self.examples[i]


def main():
    model_path = "Milos121/MMM_jsb_mmmbar"
    tokenizer_path = '../../data/external/Jazz Midi/jsb_mmmtrack/tokenizer.json'

    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    tokenizer.add_special_tokens({'pad_token': '[PAD]'})

    data_collator = DataCollatorWithPadding(
        tokenizer=tokenizer,
        padding="max_length",
        max_length=768
    )

    dataset_train = TokenSequenceDataset(
        tokenizer=tokenizer,
        dataset_paths=['../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_train.txt'],
        block_size=768,
        simulate=False
    )

    dataset_valid = TokenSequenceDataset(
        tokenizer=tokenizer,
        dataset_paths=['../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_valid.txt'],
        block_size=768,
        simulate=False
    )

    model.resize_token_embeddings(len(tokenizer))

    # Freeze all layers by default
    for param in model.parameters():
        param.requires_grad = False

    # Unfreeze the last N layers
    N = 4
    for name, param in model.named_parameters():
        if "transformer.h." in name:
            layer_number = int(name.split(".")[2])  # Extract the layer number
            if layer_number >= (model.config.n_layer - N):
                param.requires_grad = True
                print(f"Unfreezing layer {layer_number}: {name}")
            else:
                print(f"Freezing layer {layer_number}: {name}")
        else:
            print(f"Freezing non-transformer layer: {name}")

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params}/{total_params}")

    output_path = "../models"
    training_args = TrainingArguments(
    output_dir=output_path,
    overwrite_output_dir=True,
    evaluation_strategy="steps",
    save_steps=500,
    save_total_limit=2,
    logging_steps=500,
    logging_dir=os.path.join(output_path, "logs"),
    num_train_epochs=3,  # Set as needed
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    load_best_model_at_end=True,
    learning_rate=5e-5,
    weight_decay=0.01
    )

    # Filter out frozen parameters for the optimizer
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=5e-5
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset_train,
        eval_dataset=dataset_valid
    )

    trainer.train()

    finetuned_model_path = os.path.join(output_path, "finetuned_model")
    trainer.save_model(finetuned_model_path)
    print(f"Fine-tuned model saved to {finetuned_model_path}")

if __name__ == "__main__":
    main()
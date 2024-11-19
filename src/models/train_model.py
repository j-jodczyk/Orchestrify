"""
Contains script for transfer learining the model
"""

import os
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel, DataCollatorWithPadding, Trainer, TrainingArguments
from src.models.AI_GURU.token_sequence_dataset import TokenSequenceDataset

# todo: this should not be a main function - this should take arguments that will allow to reuse it efficiently
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
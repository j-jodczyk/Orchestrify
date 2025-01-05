"""
Contains script for transfer learning the model.
"""

import os
import sys

# Sometimes, it may be necessary to add the project root to ensure the imports work correctly
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# sys.path.insert(0, project_root)

from transformers import (
    PreTrainedTokenizerFast,
    GPT2LMHeadModel,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)
from src.AI_GURU.token_sequence_dataset import TokenSequenceDataset


def transfer_learn_model(
    model_path,
    tokenizer_path,
    train_dataset_path,
    valid_dataset_path,
    output_path,
    block_size=768,
    unfreeze_last_n_layers=4,
    num_train_epochs=3,
    batch_size=8,
    learning_rate=5e-5,
    weight_decay=0.01,
    save_steps=500,
    logging_steps=500,
):
    """
    Fine-tunes a pre-trained model using transfer learning.

    Args:
        model_path (str): Path to the pre-trained model.
        tokenizer_path (str): Path to the tokenizer file.
        train_dataset_path (str): Path to the training dataset.
        valid_dataset_path (str): Path to the validation dataset.
        output_path (str): Directory to save the fine-tuned model.
        block_size (int): Maximum length of token sequences. Default is 768.
        unfreeze_last_n_layers (int): Number of last layers to unfreeze for training. Default is 4.
        num_train_epochs (int): Number of epochs for training. Default is 3.
        batch_size (int): Batch size for training and evaluation. Default is 8.
        learning_rate (float): Learning rate for training. Default is 5e-5.
        weight_decay (float): Weight decay for optimizer. Default is 0.01.
        save_steps (int): Number of steps before saving a checkpoint. Default is 500.
        logging_steps (int): Number of steps before logging. Default is 500.

    Returns:
        None
    """
    model = GPT2LMHeadModel.from_pretrained(model_path)
    tokenizer = PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer, padding="max_length", max_length=block_size)

    dataset_train = TokenSequenceDataset(
        tokenizer=tokenizer,
        dataset_paths=[train_dataset_path],
        block_size=block_size,
        simulate=False,
    )
    dataset_valid = TokenSequenceDataset(
        tokenizer=tokenizer,
        dataset_paths=[valid_dataset_path],
        block_size=block_size,
        simulate=False,
    )

    model.resize_token_embeddings(len(tokenizer))

    for param in model.parameters():
        param.requires_grad = False

    # Unfreeze the last N layers
    for name, param in model.named_parameters():
        if "transformer.h." in name:
            layer_number = int(name.split(".")[2])
            if layer_number >= (model.config.n_layer - unfreeze_last_n_layers):
                param.requires_grad = True
                print(f"Unfreezing layer {layer_number}: {name}")
            else:
                print(f"Freezing layer {layer_number}: {name}")
        else:
            print(f"Freezing non-transformer layer: {name}")

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params}/{total_params}")

    training_args = TrainingArguments(
        output_dir=output_path,
        overwrite_output_dir=True,
        evaluation_strategy="steps",
        save_steps=save_steps,
        save_total_limit=2,
        logging_steps=logging_steps,
        logging_dir=os.path.join(output_path, "logs"),
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        load_best_model_at_end=True,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset_train,
        eval_dataset=dataset_valid,
    )

    trainer.train()

    finetuned_model_path = os.path.join(output_path, "finetuned_model")
    trainer.save_model(finetuned_model_path)
    print(f"Fine-tuned model saved to {finetuned_model_path}")


if __name__ == "__main__":
    model_path = "Milos121/MMM_jsb_mmmbar"
    tokenizer_path = "../../data/external/Jazz Midi/jsb_mmmtrack/tokenizer.json"
    train_dataset_path = "../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_train.txt"
    valid_dataset_path = "../../data/external/Jazz Midi/jsb_mmmtrack/token_sequences_valid.txt"
    output_path = "../models"

    transfer_learn_model(
        model_path=model_path,
        tokenizer_path=tokenizer_path,
        train_dataset_path=train_dataset_path,
        valid_dataset_path=valid_dataset_path,
        output_path=output_path,
        block_size=768,
        unfreeze_last_n_layers=4,
        num_train_epochs=3,
        batch_size=8,
        learning_rate=5e-5,
        weight_decay=0.01,
        save_steps=500,
        logging_steps=500,
    )

"""
File containing the code for reading the database, parsing, tokenizing, and training the model.
"""

import kagglehub
import os
import sys

# Sometimes, it may be necessary to add the project root to ensure the imports work correctly
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# sys.path.insert(0, project_root)

from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel

from src.data.make_dataset import make_dataset
from src.AI_GURU.mmmtrainer import MMMTrainer
from src.AI_GURU.mmmtrainerconfig import MMMTrainerBaseConfig


def train_model(
    dataset_path,
    train_file,
    valid_file,
    tokenizer_file,
    output_path,
    pad_length=768,
    shuffle_buffer_size=10000,
    batch_size=16,
    epochs=10,
    simulate=False,
):
    """
    Trains a model using the specified dataset and configuration.

    Args:
        dataset_path (str): Path to the dataset.
        train_file (str): Path to the training data file.
        valid_file (str): Path to the validation data file.
        tokenizer_file (str): Path to the tokenizer file.
        output_path (str): Directory where the trained model will be saved.
        pad_length (int): Padding length for input sequences. Default is 768.
        shuffle_buffer_size (int): Buffer size for shuffling the dataset. Default is 10000.
        batch_size (int): Batch size for training. Default is 16.
        epochs (int): Number of training epochs. Default is 10.
        simulate (bool): If True, simulates training without actual updates.

    Returns:
        None
    """
    print("Preparing dataset...")
    make_dataset(dataset_path, overwrite=False)
    print("Dataset prepared")

    trainer_config = MMMTrainerBaseConfig(
        tokenizer_path=tokenizer_file,
        dataset_train_files=[train_file],
        dataset_validate_files=[valid_file],
        pad_length=pad_length,
        shuffle_buffer_size=shuffle_buffer_size,
        batch_size=batch_size,
        epochs=epochs,
    )

    trainer = MMMTrainer(trainer_config)
    print("Trainer initialized")

    trainer.train(output_path=output_path, simulate=simulate)
    print("Training completed")


# Example usage of the function
if __name__ == "__main__":
    # dataset_path = kagglehub.dataset_download("imsparsh/lakh-midi-clean")
    # dataset_path = kagglehub.dataset_download("anujtrehan007/midi-songs")
    dataset_path = "data/test_dataset"
    train_file = os.path.join(dataset_path, "jsb_mmmbar", "token_sequences_train.txt")
    valid_file = os.path.join(dataset_path, "jsb_mmmbar", "token_sequences_valid.txt")
    tokenizer_file = os.path.join(dataset_path, "jsb_mmmbar", "tokenizer.json")
    output_path = "../models"

    train_model(
        dataset_path=dataset_path,
        train_file=train_file,
        valid_file=valid_file,
        tokenizer_file=tokenizer_file,
        output_path=output_path,
        pad_length=768,
        shuffle_buffer_size=10000,
        batch_size=16,
        epochs=10,
        simulate="simulate" in sys.argv,
    )

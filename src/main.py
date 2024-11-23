"""
File containing the code for reading db, parsing, tokenizing and training the model
"""

import kagglehub
import os
import sys
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel

from src.data.make_dataset import make_dataset
from src.AI_GURU.mmmtrainer import MMMTrainer
from src.AI_GURU.mmmtrainerconfig import MMMTrainerBaseConfig


def main():
    dataset_path = kagglehub.dataset_download("imsparsh/lakh-midi-clean")
    # dataset_path = kagglehub.dataset_download("anujtrehan007/midi-songs")
    print("Downloaded dataset")
    make_dataset(dataset_path)
    print("Dataset created")

    train_path = os.path.join(dataset_path, 'jsb_mmmtrack', 'token_sequences_train.txt')
    valid_path = os.path.join(dataset_path, 'jsb_mmmtrack', 'token_sequences_valid.txt')
    tokenizer_path = os.path.join(dataset_path, 'jsb_mmmtrack', 'tokenizer.json')

    trainer_config = MMMTrainerBaseConfig(
        tokenizer_path = tokenizer_path,
        dataset_train_files=[train_path],
        dataset_validate_files=[valid_path],
        pad_length=768,
        shuffle_buffer_size=10000,
        batch_size=16,
        epochs=10,
    )

    trainer = MMMTrainer(trainer_config)
    print("Trainer loaded")

    trainer.train(
        output_path=os.path.join("../models"),
        simulate="simulate" in sys.argv
    )
    print("Model trained")


if __name__ == "__main__":
    main()

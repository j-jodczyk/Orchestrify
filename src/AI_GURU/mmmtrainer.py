# Copyright 2021 Tristan Behrens.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3

import os
import numpy as np
import random
import torch
from typing import Dict
from torch.utils.data.dataset import Dataset
from tokenizers import Tokenizer
from transformers import DataCollatorWithPadding
from transformers import Trainer, TrainingArguments
from transformers import GPT2Config, GPT2LMHeadModel
from transformers import PreTrainedTokenizerFast
from tqdm import tqdm
from .mmmtrainerconfig import MMMTrainerBaseConfig


class MMMTrainer:
    """
    Trainer class for training GPT-2 language models with a custom dataset.

    Attributes:
        config (MMMTrainerBaseConfig): Configuration object specifying model and training parameters.
    """

    def __init__(self, config: MMMTrainerBaseConfig):
        """
        Initializes the MMMTrainer with the provided configuration.

        Args:
            config (MMMTrainerBaseConfig): Configuration for the training process.
        """

        if not isinstance(config, MMMTrainerBaseConfig) and not config.__class__.__base__ == MMMTrainerBaseConfig:
            raise Exception("Config must inherit from MMMTrainerBaseConfig")
        self.config = config

    def train(self, output_path, simulate=False):
        """
        Trains the GPT-2 model using the specified configuration.

        Args:
            output_path (str): Directory where the trained model will be saved.
            simulate (bool): If True, simulates training with a small dataset.
        """
        # Make sure the output path exists.
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if self.config.framework == "pytorch":
            return self.__train_pytorch(output_path=output_path, simulate=simulate)
        elif self.config.framework == "tensorflow":
            assert False, "Implement!"

    def __train_pytorch(self, output_path, simulate):
        """
        Implements the training process using PyTorch.

        Args:
            output_path (str): Directory where the model and logs will be saved.
            simulate (bool): If True, simulates training with a small dataset.
        """
        # Create tokenizer.
        if not os.path.exists(self.config.tokenizer_path):
            raise Exception(f"No tokenizer found at {self.config.tokenizer_path}")
        tokenizer = Tokenizer.from_file(self.config.tokenizer_path)
        pretrained_tokenizer = PreTrainedTokenizerFast(tokenizer_file=self.config.tokenizer_path)
        pretrained_tokenizer.add_special_tokens({"pad_token": "[PAD]"})

        # Create the model.
        model_config = GPT2Config(
            vocab_size=tokenizer.get_vocab_size(),
            # bos_token_id=tokenizer.token_to_id("PIECE_START"),
            # eos_token_id=tokenizer.token_to_id("PIECE_END"),
            pad_token_id=tokenizer.token_to_id("[PAD]"),
            n_head=self.config.n_head,
            n_layer=self.config.n_layer,
            n_embd=self.config.n_embd,
            n_positions=self.config.n_positions,
            n_ctx=self.config.n_ctx,
        )
        model = GPT2LMHeadModel(model_config)

        # Prepare the training dataset.
        print("Preparing training dataset...")
        dataset_train = TokenSequenceDataset(
            tokenizer=pretrained_tokenizer,
            dataset_paths=self.config.dataset_train_files,
            block_size=self.config.pad_length,
            simulate=simulate,
        )

        # Prepare the validation dataset.
        print("Preparing validate dataset...")
        dataset_valid = TokenSequenceDataset(
            tokenizer=pretrained_tokenizer,
            dataset_paths=self.config.dataset_validate_files,
            block_size=self.config.pad_length,
            simulate=simulate,
        )

        # Prepare data collator.
        data_collator = DataCollatorWithPadding(
            tokenizer=pretrained_tokenizer,
            padding="max_length",
            max_length=self.config.pad_length,
        )

        # Create the trainer.
        training_args = TrainingArguments(
            output_dir=os.path.join(output_path),
            overwrite_output_dir=True,
            evaluation_strategy="steps",
            num_train_epochs=self.config.epochs,
            per_gpu_train_batch_size=self.config.batch_size,
            save_steps=1_000,
            save_total_limit=2,
            prediction_loss_only=False,
            logging_strategy="steps",
            logging_dir=os.path.join(output_path, "logs"),
            load_best_model_at_end=True,
            save_strategy="steps",
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=dataset_train,
            eval_dataset=dataset_valid,
        )

        # Train the model.
        trainer.train()

        # Save the model.
        model_path = os.path.join(output_path, "best_model")
        trainer.save_model(model_path)


class TokenSequenceDataset(Dataset):
    """
    Custom dataset class for tokenized sequences used in training.

    Attributes:
        tokenizer (PreTrainedTokenizerFast): Tokenizer used for encoding.
        examples (list): List of encoded sequences with padding and truncation applied.
    """

    def __init__(self, tokenizer, dataset_paths, block_size, simulate=False):
        """
        Initializes the TokenSequenceDataset.

        Args:
            tokenizer (PreTrainedTokenizerFast): Tokenizer for encoding sequences.
            dataset_paths (list): List of paths to input dataset files.
            block_size (int): Maximum sequence length after padding.
            simulate (bool): If True, uses a smaller dataset for simulation.
        """

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
        for line in tqdm(lines):

            # Skip empty lines.
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
                # logger.warning(f"Skipping line because of unknown token {token}")
                unknown_tokens += [token]
                unknown_token_lines_count += 1
                continue

            # Skip sequence if it is too long.
            if len(encoded_line) > block_size:
                # logger.warning(f"Skipping line because it is too long... {len(encoded_line)} > {block_size}")
                too_long_lines_count += 1
                continue

            # Pad and truncate.
            tensor = np.full((block_size,), pad_token_id, dtype=np.longlong)
            tensor[: len(encoded_line)] = encoded_line
            assert len(tensor) == block_size

            self.examples += [
                {
                    "input_ids": torch.tensor(tensor, dtype=torch.long),
                    "labels": torch.tensor(tensor, dtype=torch.long),
                }
            ]

    def __len__(self):
        """
        Returns the number of examples in the dataset.
        """
        return len(self.examples)

    def __getitem__(self, i) -> Dict[str, torch.tensor]:
        """
        Retrieves the i-th example from the dataset.

        Args:
            i (int): Index of the example to retrieve.

        Returns:
            Dict[str, torch.tensor]: Encoded sequence and labels.
        """
        return self.examples[i]

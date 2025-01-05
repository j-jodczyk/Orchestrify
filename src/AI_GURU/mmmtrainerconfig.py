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


class MMMTrainerBaseConfig:
    """
    Base configuration class for the MMMTrainer.

    Attributes:
        framework (str): Framework to use for training (default: "pytorch").
        tokenizer_path (str): Path to the tokenizer file.
        dataset_train_files (list): List of paths to training dataset files.
        dataset_validate_files (list): List of paths to validation dataset files.
        pad_length (int): Maximum padding length for input sequences.
        shuffle_buffer_size (int): Buffer size for shuffling datasets.
        batch_size (int): Batch size for training.
        epochs (int): Number of training epochs.
        n_head (int): Number of attention heads in the model.
        n_layer (int): Number of transformer layers.
        n_embd (int): Dimension of the embedding space.
        n_positions (int): Maximum number of positional encodings.
        n_ctx (int): Context size for input sequences.
    """

    def __init__(
        self,
        framework="pytorch",
        tokenizer_path="",
        dataset_train_files=[],
        dataset_validate_files=[],
        pad_length=768,
        shuffle_buffer_size=10000,
        batch_size=8,
        epochs=10,
        n_head=8,
        n_layer=6,
        n_embd=512,
        n_positions=1024,
        n_ctx=1024,
    ):
        """
        Initializes the MMMTrainerBaseConfig with the provided parameters.

        Args:
            framework (str): Framework to use for training. Default is "pytorch".
            tokenizer_path (str): Path to the tokenizer file.
            dataset_train_files (list): List of training dataset file paths.
            dataset_validate_files (list): List of validation dataset file paths.
            pad_length (int): Maximum length of sequences after padding.
            shuffle_buffer_size (int): Buffer size for dataset shuffling.
            batch_size (int): Batch size for training.
            epochs (int): Number of training epochs.
            n_head (int): Number of attention heads.
            n_layer (int): Number of transformer layers.
            n_embd (int): Dimension of embedding vectors.
            n_positions (int): Maximum number of positions for positional encoding.
            n_ctx (int): Maximum context size for input sequences.

        Raises:
            Exception: If the framework is invalid or dataset files are missing.
            AssertionError: If `pad_length` exceeds `n_positions`.
        """

        # Check if the framework is valid.
        valid_frameworks = ["pytorch"]
        if framework not in valid_frameworks:
            error_string = f"Invalid framework {framework}. Expected one of {valid_frameworks}."
            raise Exception(error_string)

        # Check if any dataset files are missing.
        missing_dataset_files = []
        missing_dataset_files = [
            file for file in dataset_train_files + dataset_validate_files if not os.path.exists(file)
        ]
        if len(missing_dataset_files) != 0:
            error_string = f"Missing dataset files {missing_dataset_files}."
            raise Exception(error_string)

        assert pad_length <= n_positions

        self.framework = framework
        self.tokenizer_path = tokenizer_path
        self.dataset_train_files = dataset_train_files
        self.dataset_validate_files = dataset_validate_files
        self.pad_length = pad_length
        self.shuffle_buffer_size = shuffle_buffer_size
        self.batch_size = batch_size
        self.epochs = epochs
        self.n_head = n_head
        self.n_layer = n_layer
        self.n_embd = n_embd
        self.n_positions = n_positions
        self.n_ctx = n_ctx


class JSBTrackConfig(MMMTrainerBaseConfig):
    """
    Configuration class for JSB Track-level dataset training.

    Inherits from MMMTrainerBaseConfig and allows additional arguments to override default values.
    """

    def __init__(self, **kwargs):
        """
        Initializes the JSBTrackConfig.

        Args:
            **kwargs: Additional arguments to override default configuration parameters.
        """
        super().__init__(**kwargs)


class JSBBarConfig(MMMTrainerBaseConfig):
    """
    Configuration class for JSB Bar-level dataset training.

    Inherits from MMMTrainerBaseConfig and allows additional arguments to override default values.
    """

    def __init__(self, **kwargs):
        """
        Initializes the JSBBarConfig.

        Args:
            **kwargs: Additional arguments to override default configuration parameters.
        """
        super().__init__(**kwargs)

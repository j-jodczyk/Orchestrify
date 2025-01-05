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
from . import logging
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import WhitespaceSplit
from tokenizers.trainers import WordLevelTrainer
from .preprocess.music21jsb import preprocess_music21
from .preprocess.encode import encode_songs_data, get_density_bins

logger = logging.create_logger("datasetcreator")


class DatasetCreator:
    """
    A class responsible for creating datasets for MMM model.

    Attributes:
        config: Configuration object specifying dataset creation parameters.
    """

    def __init__(self, config):
        """
        Initializes the DatasetCreator with a given configuration.

        Args:
            config: Configuration object with parameters for dataset creation.
        """
        self.config = config

    def create(self, datasets_path, overwrite=False):
        """
        Initializes the DatasetCreator with a given configuration.

        Args:
            config: Configuration object with parameters for dataset creation.
        """
        # Ensure dataset paths exist
        dataset_path = self.__prepare_paths(datasets_path, overwrite)

        if dataset_path is None and not overwrite:
            return

        # Prepare for getting music data as JSON
        json_data_method, preprocess_with_music21 = self.__resolve_json_data_method()

        # Get all MIDI files
        all_midi_files = self.__get_all_midi_files(datasets_path)

        # Process and save data with appropriate method
        if preprocess_with_music21:
            self.__process_with_music21(all_midi_files, dataset_path, overwrite)
        else:
            songs_data_train, songs_data_valid = json_data_method()
            self.__process_and_save_data(songs_data_train, songs_data_valid, dataset_path)

    def __prepare_paths(self, datasets_path, overwrite):
        """
        Prepares the necessary directories for dataset creation.

        Args:
            datasets_path (str): Path to the datasets folder.
            overwrite (bool): Whether to overwrite existing datasets.

        Returns:
            str: Path to the dataset directory or None if dataset already exists.
        """
        if not os.path.exists(datasets_path):
            raise Exception("Dataset path doesn't exist")

        dataset_path = os.path.join(datasets_path, self.config.dataset_name)
        if os.path.exists(dataset_path) and not overwrite:
            logger.info("Dataset already exists.")
            return None

        if not os.path.exists(dataset_path):
            os.makedirs(dataset_path)
        return dataset_path

    def __resolve_json_data_method(self):
        """
        Determines the method to process JSON data based on the configuration.

        Returns:
            tuple: A method for generating JSON data and a boolean indicating
            whether to use music21 preprocessing.
        """
        if self.config.json_data_method == "preprocess_music21":
            return None, True
        elif callable(self.config.json_data_method):
            return self.config.json_data_method, False
        else:
            error_string = f"Unexpected {self.config.json_data_method}."
            logger.error(error_string)
            raise Exception(error_string)

    def __get_all_midi_files(self, datasets_path):
        """
        Retrieves all MIDI files from the specified path.

        Args:
            datasets_path (str): Path to the datasets folder.

        Returns:
            list: A list of paths to MIDI files.
        """
        midi_files_path = os.path.join(datasets_path, "midi_files")

        if not os.path.exists(midi_files_path):
            raise FileNotFoundError("Please create a 'midi_files' folder with all the MIDI files.")

        return [
            os.path.join(midi_files_path, f)
            for f in os.listdir(midi_files_path)
            if f.endswith(".mid")
        ]

    def __process_with_music21(self, all_midi_files, dataset_path, overwrite):
        """
        Processes MIDI files using the music21 library and saves the results.

        Args:
            all_midi_files (list): List of paths to MIDI files.
            dataset_path (str): Path to the dataset directory.
            overwrite (bool): Whether to overwrite existing files.
        """
        batch_size = 100
        total_batches = (len(all_midi_files) + batch_size - 1) // batch_size
        print(dataset_path)
        train_file_path = os.path.join(dataset_path, "token_sequences_train.txt")
        valid_file_path = os.path.join(dataset_path, "token_sequences_valid.txt")

        if overwrite:
            open(train_file_path, "w").close()
            open(valid_file_path, "w").close()

        batch_index = 0
        while True:
            start_idx = batch_index * batch_size
            end_idx = start_idx + batch_size
            midi_files_batch = all_midi_files[start_idx:end_idx]

            if not midi_files_batch:
                break

            logger.info(f"Processing batch {batch_index + 1} of {total_batches} with {len(midi_files_batch)} files.")
            songs_data_train, songs_data_valid, is_done = preprocess_music21(midi_files_batch)

            if not songs_data_train and not songs_data_valid:
                batch_index += 1
                if is_done:
                    break
                continue

            density_bins = get_density_bins(
                songs_data_train,
                self.config.window_size_bars,
                self.config.hop_length_bars,
                self.config.density_bins_number,
            )

            self.__append_encoded_data(
                songs_data_train, train_file_path, density_bins, self.config.transpositions_train
            )
            logger.info(f"Appended training data for batch {batch_index} to {train_file_path}.")

            self.__append_encoded_data(songs_data_valid, valid_file_path, density_bins, [0])
            logger.info(f"Appended validation data for batch {batch_index} to {valid_file_path}.")

            if is_done:
                break
            batch_index += 1

        tokenizer = self.__create_and_save_tokenizer([train_file_path], dataset_path)

    def __process_and_save_data(self, songs_data_train, songs_data_valid, dataset_path):
        """
        Processes and saves training and validation data.

        Args:
            songs_data_train: Training data.
            songs_data_valid: Validation data.
            dataset_path (str): Path to the dataset directory.
        """
        density_bins = get_density_bins(
            songs_data_train, self.config.window_size_bars, self.config.hop_length_bars, self.config.density_bins_number
        )

        train_file_path = os.path.join(dataset_path, "token_sequences_train.txt")
        self.__save_encoded_data(songs_data_train, train_file_path, density_bins, self.config.transpositions_train)

        valid_file_path = os.path.join(dataset_path, "token_sequences_valid.txt")
        self.__save_encoded_data(songs_data_valid, valid_file_path, density_bins, [0])

        self.__create_and_save_tokenizer([train_file_path, valid_file_path], dataset_path)

    def __save_encoded_data(self, songs_data, path, density_bins, transpositions):
        """
        Encodes and saves song data to a file.

        Args:
            songs_data: Data to encode.
            path (str): File path to save data.
            density_bins: Density bins for encoding.
            transpositions (list): List of transpositions for augmentation.
        """
        token_sequences = encode_songs_data(
            songs_data,
            transpositions=transpositions,
            permute=self.config.permute_tracks,
            window_size_bars=self.config.window_size_bars,
            hop_length_bars=self.config.hop_length_bars,
            density_bins=density_bins,
            bar_fill=False,
        )
        self.__save_token_sequences(token_sequences, path)

    def __append_encoded_data(self, songs_data, path, density_bins, transpositions):
        """
        Encodes and appends song data to a file.

        Args:
            songs_data: Data to encode.
            path (str): File path to append data.
            density_bins: Density bins for encoding.
            transpositions (list): List of transpositions for augmentation.
        """
        token_sequences = encode_songs_data(
            songs_data,
            transpositions=transpositions,
            permute=self.config.permute_tracks,
            window_size_bars=self.config.window_size_bars,
            hop_length_bars=self.config.hop_length_bars,
            density_bins=density_bins,
            bar_fill=False,
        )
        self.__append_token_sequences(token_sequences, path)

    def __save_token_sequences(self, token_sequences, path):
        """
        Saves token sequences to a file.

        Args:
            token_sequences: List of token sequences.
            path (str): File path to save the sequences.
        """
        with open(path, "w") as file:
            for token_sequence in token_sequences:
                print(" ".join(token_sequence), file=file)

    def __append_token_sequences(self, token_sequences, path):
        """
        Appends token sequences to a file.

        Args:
            token_sequences: List of token sequences.
            path (str): File path to append the sequences.
        """
        with open(path, "a") as file:
            for token_sequence in token_sequences:
                file.write(" ".join(token_sequence) + "\n")

    def __create_and_save_tokenizer(self, files, dataset_path):
        """
        Creates and saves a tokenizer for the dataset.

        Args:
            files (list): List of files to use for training the tokenizer.
            dataset_path (str): Path to save the tokenizer.
        """
        tokenizer = self.__create_tokenizer(files)
        tokenizer_path = os.path.join(dataset_path, "tokenizer.json")
        tokenizer.save(tokenizer_path)

    def __create_tokenizer(self, files):
        """
        Creates a tokenizer from the given files.

        Args:
            files (list): List of files to train the tokenizer.

        Returns:
            Tokenizer: A trained tokenizer object.
        """
        logger.info("Preparing tokenizer...")
        tokenizer = Tokenizer(WordLevel(unk_token="[UNK]"))
        tokenizer.pre_tokenizer = WhitespaceSplit()
        trainer = WordLevelTrainer(special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])
        tokenizer.train(files=files, trainer=trainer)
        return tokenizer

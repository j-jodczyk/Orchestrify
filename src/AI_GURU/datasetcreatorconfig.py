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
from src.AI_GURU.logging import create_logger

logger = create_logger("datasetcreatorconfig")


class DatasetCreatorBaseConfig:
    """
    Base class for dataset creator configuration.

    Attributes:
        dataset_name (str): Name of the dataset.
        encoding_method (str/callable): Method or string specifying the encoding type.
        json_data_method (str/callable): Method or string for JSON data processing.
        window_size_bars (int): Window size in bars for encoding.
        hop_length_bars (int): Hop length in bars for sliding windows.
        density_bins_number (int): Number of bins for density calculation.
        transpositions_train (list): List of integers representing transpositions.
        permute_tracks (bool): Whether to permute tracks during preprocessing.
    """

    def __init__(
        self,
        dataset_name,
        encoding_method,
        json_data_method,
        window_size_bars,
        hop_length_bars,
        density_bins_number,
        transpositions_train,
        permute_tracks,
    ):
        """
        Initializes the DatasetCreatorBaseConfig and validates its parameters.

        Args:
            dataset_name (str): Name of the dataset.
            encoding_method (str/callable): Encoding method or string identifier.
            json_data_method (str/callable): JSON data processing method or string.
            window_size_bars (int): Sliding window size in bars.
            hop_length_bars (int): Hop length in bars.
            density_bins_number (int): Number of density bins.
            transpositions_train (list): List of integers for training transpositions.
            permute_tracks (bool): Whether to permute tracks in preprocessing.
        """

        # Check if the datasetname is fine.
        if not isinstance(dataset_name, str):
            error_string = f"Config parameter dataset_name {dataset_name} must be a string."
            logger.error(error_string)
            raise Exception(error_string)

        # Check if the encoding is fine.
        if not isinstance(encoding_method, str) and not callable(encoding_method):
            error_string = f"Config parameter encoding_method {encoding_method} must be a string or a method."
            logger.error(error_string)
            raise Exception(error_string)

        # Check if the json data method is fine.
        if not isinstance(json_data_method, str) and not callable(json_data_method):
            error_string = f"Config parameter json_data_method {json_data_method} must be a string or a method."
            logger.error(error_string)
            raise Exception(error_string)

        if not isinstance(window_size_bars, int) or window_size_bars == 0:
            error_string = f"Config parameter window_size_bars must be a non zero integer, but is {window_size_bars}."
            logger.error(error_string)
            raise Exception(error_string)

        if not isinstance(hop_length_bars, int) or hop_length_bars == 0:
            error_string = f"Config parameter hop_length_bars must be a non zero integer, but is {hop_length_bars}."
            logger.error(error_string)
            raise Exception(error_string)

        if not isinstance(density_bins_number, int) or density_bins_number == 0:
            error_string = (
                f"Config parameter density_bins_number must be a non zero integer, but is {density_bins_number}."
            )
            logger.error(error_string)
            raise Exception(error_string)

        if not isinstance(transpositions_train, list):
            error_string = (
                f"Config parameter transpositions_train must be a list of integers, but is {density_bins_number}."
            )
            logger.error(error_string)
            raise Exception(error_string)

        if not isinstance(permute_tracks, bool):
            error_string = f"Config parameter permute_tracks must be a boolean, but is {permute_tracks}."
            logger.error(error_string)
            raise Exception(error_string)

        # Assign.
        self.dataset_name = dataset_name
        self.encoding_method = encoding_method
        self.json_data_method = json_data_method
        self.window_size_bars = window_size_bars
        self.hop_length_bars = hop_length_bars
        self.density_bins_number = density_bins_number
        self.transpositions_train = transpositions_train
        self.permute_tracks = permute_tracks


class JSBDatasetCreatorTrackConfig(DatasetCreatorBaseConfig):
    """
    Configuration for creating track-level datasets from the JSB dataset.

    Inherits from `DatasetCreatorBaseConfig` and sets default parameters specific
    to track-level encoding.
    """

    def __init__(self, **kwargs):
        """
        Initializes the track-level dataset configuration with default values.

        Args:
            **kwargs: Additional arguments to override default parameters.
        """
        super().__init__(
            dataset_name="jsb_mmmtrack",
            encoding_method="mmmtrack",
            json_data_method="preprocess_music21",
            window_size_bars=2,
            hop_length_bars=2,
            density_bins_number=5,
            transpositions_train=list(range(-12, 13)),
            permute_tracks=True,
            **kwargs,
        )


class JSBDatasetCreatorBarConfig(DatasetCreatorBaseConfig):
    """
    Configuration for creating bar-level datasets from the JSB dataset.

    Inherits from `DatasetCreatorBaseConfig` and sets default parameters specific
    to bar-level encoding.
    """

    def __init__(self, **kwargs):
        """
        Initializes the bar-level dataset configuration with default values.

        Args:
            **kwargs: Additional arguments to override default parameters.
        """
        super().__init__(
            dataset_name="jsb_mmmbar",
            encoding_method="mmmbar",
            json_data_method="preprocess_music21",
            window_size_bars=2,
            hop_length_bars=2,
            density_bins_number=5,
            transpositions_train=list(range(-12, 13)),
            permute_tracks=True,
            **kwargs,
        )

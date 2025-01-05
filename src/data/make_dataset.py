"""
This script contains the functionality to create a dataset using the JSBDatasetCreatorBar configuration.
It initializes the necessary configurations and creates the dataset in the specified path.
"""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.AI_GURU.datasetcreator import DatasetCreator
from src.AI_GURU.datasetcreatorconfig import JSBDatasetCreatorBarConfig

def make_dataset(datasets_path: str, overwrite: bool = False):
    """
    Creates a dataset using the JSBDatasetCreatorBar configuration.

    Args:
        datasets_path (str): The path where the dataset should be created.
        overwrite (bool, optional): If True, overwrites any existing datasets at the specified path. Defaults to False.

    Returns:
        None: This function does not return any value.
    """
    dataset_creator_config = JSBDatasetCreatorBarConfig()
    dataset_creator = DatasetCreator(dataset_creator_config)
    dataset_creator.create(datasets_path, overwrite)
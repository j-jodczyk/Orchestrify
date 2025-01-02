
from AI_GURU.datasetcreator import DatasetCreator
from AI_GURU.datasetcreatorconfig import JSBDatasetCreatorBarConfig

def make_dataset(datasets_path: str, overwrite: bool=False):
	dataset_creator_config = JSBDatasetCreatorBarConfig()
	dataset_creator = DatasetCreator(dataset_creator_config)
	dataset_creator.create(datasets_path, overwrite)

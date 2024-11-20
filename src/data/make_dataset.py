
import datasetcreator
import datasetcreatorconfig

def main():
	dataset_creator_config = datasetcreatorconfig.JSBDatasetCreatorTrackConfig()
	dataset_creator = datasetcreator.DatasetCreator(dataset_creator_config)
	dataset_creator.create(datasets_path='../data/external/Jazz Midi', overwrite=False)

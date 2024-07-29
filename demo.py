from house.pipeline.pipeline import Pipelines
from house.exception import HouseException
from house.logger import logging
from house.component.data_ingestion import DataIngestion
from house.config.configuration import Configuration
import os
from house.component.data_validation import DataValidation
from house.component.data_transformation import DataTransformation
from house.entity.artifact_entity import DataIngestionArtifact,DataTransformationArtifact
from house.entity.config_entity import DataValidationConfig,DataTransformationConfig

def main():
   
    pipelines= Pipelines()
    pipelines.run_pipeline()
    #data_validation=DataValidation(DataValidationConfig,DataIngestionArtifact).is_train_test_file_exists()
    #print(data_validation)
    #data_transformation=Configuration().get_data_transformation_config()
    #print(data_transformation)
    
    
if __name__=="__main__":
    main()
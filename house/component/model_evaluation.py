from house.logger import logging
from house.exception import HouseException
from house.entity.config_entity import ModelEvaluationConfig
from house.entity.artifact_entity import DataIngestionArtifact , DataValidationArtifact, DataTransformationArtifact,ModelEvaluationArtifact
from house.constant import *
import numpy as np
import os
import sys
from house.util.util import write_yaml_file, read_yaml_file, load_object, load_data
from house.entity.model_factory import evaluate_regression_model

class ModelEvaluation:
    def __init__(self,model_evaluation_config: ModelEvaluationConfig,
                 data_ingestion_artifact :DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        
        
        





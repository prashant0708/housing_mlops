from house.exception import HouseException
from house.logger import logging
import sys
from typing import List
from house.entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from house.entity.config_entity import ModelTrainerConfig
from house.util.util import load_numpy_array_data , save_object,load_object
from house.entity.model_factory import MetricInfoArtifact, ModelFactory, GridSearchedBestModel
from house.entity.model_factory import evaluate_regression_model

class HousingEstimatorModel:
    def __init__(self, preprocessing_object, trained_model_object):
        
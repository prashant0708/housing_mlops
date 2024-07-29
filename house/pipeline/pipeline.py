from collections import namedtuple
from datetime import datetime
import uuid
import os,sys
import pandas as pd
from typing import List
from threading import Thread
from multiprocessing import Process


from house.config.configuration import  Configuration
from house.logger import logging , get_log_file_name
from house.exception import HouseException
from house.entity.artifact_entity import DataIngestionArtifact ,DataValidationArtifact,DataTransformationArtifact,ModelEvaluationArtifact,ModelTrainerArtifact,ModelPusherArtifact
from house.entity.config_entity import DataIngestionConfig,ModelEvaluationConfig
from house.component.data_ingestion import DataIngestion
from house.component.data_validation import DataValidation
from house.component.data_transformation import DataTransformation
from house.component.model_trainer import ModelTrainer
from house.component.model_evaluation import ModelEvaluation
from house.component.model_pusher import ModelPusher
from house.constant import EXPERIMENT_DIR_NAME , EXPERIMENT_FILE_NAME

Experiment = namedtuple("Experiment",["experiment_id","initialized_timestamp","artifact_time_stamp",
                                      "running_status","start_time","stop_time","execution_time","message",
                                      "experiment_file_path","accuracy","is_model_accepted"])




class Pipelines:
    experiment:Experiment = Experiment(*([None]*11))
    experiment_file_path=None


    def __init__(self, config=Configuration())->None:
        try :
            self.config=config  
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            data_ingestion = DataIngestion(data_ingestion_config=self.config)
            return data_ingestion.initiate_data_ingestion()
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            data_validation = DataValidation(data_validation_config=self.config.get_data_validation_config(),
                                             data_ingestion_artifact=data_ingestion_artifact
                                             )
            return data_validation.initiate_data_validation()
        except Exception as e:
            raise HouseException(e, sys) from e
        
    def start_data_transformation(self,data_ingestion_artifact:DataIngestionArtifact,
                                       data_validation_artifact:DataValidationArtifact)->DataTransformationArtifact:
        
        try:
            data_transformation= DataTransformation(data_transformation_config=self.config.get_data_transformation_config(),
                                                    data_ingestion_artifact=data_ingestion_artifact,
                                                    data_validation_artifact=data_validation_artifact)
            
            return data_transformation.initiate_data_transformation()
        
        except Exception as e:
            raise HouseException(e,sys)
        
    def start_model_trainer(self,data_transformation_artifact:DataTransformationArtifact)-> ModelTrainerArtifact:
        try:
            model_trainer= ModelTrainer(model_trainer_config=self.config.get_model_trainer_config(),
                                        data_transformation_artifact=data_transformation_artifact)
            
            return model_trainer.initiate_model_trainer()
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def start_model_evaluation(self,data_ingestion_artifact:DataIngestionArtifact,
                               data_validation_artifact:DataValidationArtifact,
                               model_trainer_artifact:ModelTrainerArtifact)->ModelEvaluationArtifact:
        try:
            model_eval=ModelEvaluation(
                model_evaluation_config=self.config.get_model_evaluation_config(),
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_artifact=data_validation_artifact,
                model_trainer_artifact=model_trainer_artifact)
            return model_eval.initiate_model_evaluation()
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def start_model_pusher(self,model_eval_artifact: ModelEvaluationArtifact)->ModelPusherArtifact:
        try:
            model_pusher=ModelPusher(model_pusher_config=self.config.get_model_pusher_config(),
                                     model_evaluation_artifact=model_eval_artifact)
            return model_pusher.initiate_model_pusher()
        except Exception as e:
            raise HouseException(e,sys) from e
            
        
    def run_pipeline(self):
        try:
             ## dataingestion
                
            data_ingestion_artifact=self.start_data_ingestion()
            data_validation_artifact=self.start_data_validation(data_ingestion_artifact)
            data_transformation_artifact=self.start_data_transformation(data_ingestion_artifact,
                                                                        data_validation_artifact)
            
            model_trainer_artifact=self.start_model_trainer(data_transformation_artifact)
            model_evaluation_artifact=self.start_model_evaluation(data_ingestion_artifact,
                                                                  data_validation_artifact,
                                                                  model_trainer_artifact)
            
            if model_evaluation_artifact.is_model_accepted:
                model_pusher_artifact=self.start_model_pusher(model_evaluation_artifact)
                logging.info(f"Model pusher artifact: {model_pusher_artifact}")
            else:
                logging.info("Trained model rejected")
            logging.info("Pipeline completed")
        except Exception as e:
            raise HouseException(e,sys) from e
            
            
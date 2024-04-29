from house.config.configuration import  Configuration
from house.logger import logging
from house.exception import HouseException

from house.entity.artifact_entity import DataIngestionArtifact
from house.entity.config_entity import DataIngestionConfig
from house.component.data_ingestion import DataIngestion

import os,sys

class Pipelines:


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
            
        

    def run_pipeline(self):
        try:
             ## dataingestion
                
            data_ingestion_artifact=self.start_data_ingestion()
        except Exception as e:
            raise HouseException(e,sys) from e
            
            
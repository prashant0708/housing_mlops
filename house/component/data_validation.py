from profile import Profile
from house.logger import logging
from house.exception import HouseException
from house.entity.config_entity import DataValidationConfig
from house.component.data_ingestion import DataIngestion
from house.entity.artifact_entity import DataValidationArtifact
from house.config.configuration import Configuration
from house.component.data_ingestion import DataIngestionArtifact
import os,sys
import pandas as pd

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab
import json

class DataValidation :
    
    def __init__(self,data_validation_config:DataValidationConfig,
                 data_ingestion_artifact:DataIngestionArtifact) -> None:
        try:
            self.data_validation_config=data_validation_config
            self.data_ingestion_artifact=data_ingestion_artifact
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def get_train_and_test_df(self):
        try:
            train_df=pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df=pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df,test_df
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def is_train_test_file_exists(self)->bool:
        try:
            logging.info("checking if training and test file are available")
            is_train_file_exists=False
            is_test_file_exists=False
            train_file_path=self.data_ingestion_artifact.train_file_path
            test_file_path=self.data_ingestion_artifact.test_file_path
            is_train_file_exists=os.path.exists(train_file_path)
            is_test_file_exists=os.path.exists(test_file_path)
            
            is_available=is_train_file_exists and is_test_file_exists
            logging.info(f"Is train and test file exists? -> {is_available}")
            if not is_available:
                training_file=self.data_ingestion_artifact.train_file_path
                test_file=self.data_ingestion_artifact.test_file_path
                message=f"Training file:{training_file}or Test file:{test_file}is not present"
                logging.info(message)
                raise Exception(message)
            
            return is_available
        except Exception as e:
            raise HouseException(e,sys) from e
        
    
    def validate_dataset_schema(self)->bool:
        try:
            validation_status=False
            
            validation_status=True
            return validation_status
        except Exception as e:
            raise HouseException(e,sys) from e
    
    def get_and_save_data_drift_report(self):
        try:
            profile=Profile(sections=[DataDriftProfileSection()])
            train_df,test_df=self.get_train_and_test_df()
            profile.calculate(train_df,test_df)
            profile.json()
            report=json.loads(profile.json())
            
            report_file_path = self.data_validation_config.report_file_path
            report_dir=os.path.dirname(report_file_path)
            
            
            os.makedirs(report_dir,exist_ok=True)
            
            ## below line of code will write the report to data validation location
            with open(report_file_path ,"w") as report_file:
                json.dump(report,report_file,indent=6)
                
            return report
            
        except Exception as e:
            raise HouseException(e,sys) from e
    
    def save_data_drift_report_page(self):
        try:
            dashboard=Dashboard(tabs=[DataDriftTab()])
            train_df,test_df=self.get_train_and_test_df()
            dashboard.calculate(train_df,test_df)
            dashboard.save(self.data_validation_config.report_page_file_path)
        except Exception as e:
            raise HouseException(e,sys) from e
        
    def is_data_drift_found(self):
        try:
            report= self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        except Exception as e:
            raise HouseException(e,sys) from e
        
    
    def initiate_data_validation(self)->DataValidationArtifact:
        try:
            self.is_train_test_file_exists()
            self.validate_dataset_schema()
            self.is_data_drift_found()
            
            data_validation_artifact=DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successfully"
            )
            
            
            logging.info(f"Data Validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise HouseException(e,sys) from e
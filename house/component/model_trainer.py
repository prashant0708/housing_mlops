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
        """
        Training Model Constructor

        Args:
            preprocessing_object : preprocessing_object
            trained_model_object : trained_model_object
        """
        self.preprocessing_object = preprocessing_object
        self.trained_model_object = trained_model_object
        
    def predict(self,x):
        """
        Function accepts raw input and then transformed raw input using preprocessing_object
        which guarantees that the input are in the sae format as the training data
        At last it perform prediction on transformed features
        """
        
        transformed_feature = self.preprocessing_object.transform(x)
        return  self.trained_model_object.predict(transformed_feature)
    
    def __repr__(self): # __repr__ method is used to define a string representation of the object , it return the string that can be recreate as object. it help in debugging. 
        return f"{type(self.trained_model_object).__name__}()"
    
    def __str__(self): # __str__ method in your class to provide a user-friendly string representation.
        return f"{type(self.trained_model_object).__name__}()"
    
    
    
class ModelTrainer:
    
    def __init__(self,model_trainer_config:ModelTrainerConfig,data_transformation_artifact: DataTransformationArtifact):
        try:
            logging.info(f"{'>>'*30}Model trainer log started.{'<<'*30}")
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact 
        except Exception as e:
            raise HouseException(e, sys) from e
        
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            logging.info(f"Loading transformed training dataset")
            transformed_train_file_path = self.data_transformation_artifact.transformed_train_file_path
            train_array = load_numpy_array_data(file_path=transformed_train_file_path)
            
            logging.info(f"Loading the transformed testing dataset")
            transformed_test_file_path = self.data_transformation_artifact.transformed_test_file_path
            test_array = load_numpy_array_data(file_path=transformed_test_file_path)
            
            logging.info(f"Splitting training and testing input and target feature")
            x_train,y_train,x_test,y_test= train_array[:,:-1],train_array[:,-1],test_array[:,:-1],test_array[:,-1]
            
            logging.info(f"Extracting the model config file path")
            model_config_file_path= self.model_trainer_config.model_config_file_path
            
            logging.info(f"Initializing model factory class using above model config file :{model_config_file_path}")
            
            model_factory=ModelFactory(model_config_path=model_config_file_path)
            
            base_accuracy = self.model_trainer_config.base_accuracy
            logging.info(f"Expected accuracy: {base_accuracy}")
            
            logging.info(f"Initiating operation model selection")
            best_model = model_factory.get_best_model(x=x_train,y=y_train,base_accuracy=base_accuracy)
            
            logging.info(f"Best model found on training dataset: {best_model}")
            
            logging.info(f"Extracting trained model list")
            grid_searched_best_model_list:List[GridSearchedBestModel]=model_factory.grid_searched_best_model_list
            
            model_list = [model.best_model for model in grid_searched_best_model_list]
            logging.info(f"Evaluation all trained model on training and testing dataset both")
            metric_info:MetricInfoArtifact = evaluate_regression_model(model_list=model_list,x_train=x_train,y_train=y_train,x_test=x_test,y_test=y_test,base_accuracy=base_accuracy)
            
            logging.info(f"Best found model on both training and testing dataset.")
            
            preprocessing_obj=load_object(file_path=self.data_transformation_artifact.preprocessed_object_file_path)
            model_object = metric_info.model_object
            
            trained_model_file_path = self.model_trainer_config.trained_model_file_path
            housing_model=HousingEstimatorModel(preprocessing_object=preprocessing_obj,trained_model_object=model_object)
            logging.info(f"saving model at path:{trained_model_file_path}")
            save_object(file_path=trained_model_file_path,obj=housing_model)
            
            
            model_trainer_artifact = ModelTrainerArtifact(is_trained=True,message="Model Trained successfully",
                                                          trained_model_file_path=trained_model_file_path,
                                                          train_rmse=metric_info.train_rmse,
                                                          test_rmse=metric_info.test_rmse,
                                                          train_accuracy=metric_info.train_accuracy,
                                                          test_accuracy=metric_info.test_accuracy,
                                                          model_accuracy=metric_info.model_accuracy)
            
            logging.info(f"Model Trainer Artifact{model_trainer_artifact}")
            return model_trainer_artifact   
        except Exception as e:
            raise HouseException(e, sys) from e
        
    def __del__(self):
        logging.info(f"{'>>' * 30}Model trainer log completed.{'<<' * 30} ")
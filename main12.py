from flask import Flask, request
from flask import send_file ,abort,render_template
import os,sys
import pip
import json
from house.exception import HouseException
from house.logger import logging
from house.logger import get_log_dataframe
from house.config.configuration import Configuration
from house.constant import *
from house.pipeline.pipeline import Pipelines
from house.entity.housing_predictors import HousingPredictor,HousingData
from house.util.util import read_yaml_file,write_yaml_file
from matplotlib.style import context
import  pandas as pd
import numpy as np


ROOT_DIR=os.getcwd()
LOG_FOLDER_NAME="housing_logs"
PIPELINE_FOLDER_NAME="house"
SAVED_MODEL_DIR_NAME="saved_models"
MODEL_CONFIG_FILE_PATH=os.path.join(ROOT_DIR,CONFIG_DIR,"model.yaml")
LOG_DIR=os.path.join(ROOT_DIR,LOG_FOLDER_NAME)
PIPELINE_DIR=os.path.join(ROOT_DIR,PIPELINE_FOLDER_NAME)
MODEL_DIR=os.path.join(ROOT_DIR,SAVED_MODEL_DIR_NAME)

HOUSING_DATA_KEY="data"
MEDIAN_HOUSING_VALUE_KEY="median_housing_value"

app= Flask(__name__)
@app.route('/',methods=['GET','POST'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return str(e)
    
@app.route('/view_experiment_hist',methods=['GET','POST'])
def view_experiment_history():
    experiment_df =Pipelines.get_experiments_status()
    context={
        "experiment": experiment_df.to_html(classes='table table-striped col-12')
    }
    
    return render_template('experiment_history.html',context=context)


@app.route('/predict',methods=['GET','POST'])
def predict():
    context={
        HOUSING_DATA_KEY:None,
        MEDIAN_HOUSING_VALUE_KEY:None
    }
    if request.method=='POST':
        longitude=float(request.form['longitude'])
        latitude=float(request.form['latitude'])
        housing_median_age=float(request.form['housing_median_age'])
        total_rooms=float(request.form['total_rooms'])
        total_bedrooms=float(request.form['total_bedrooms'])
        population=float(request.form['population'])
        households=float(request.form['households'])
        median_income=float(request.form['median_income'])
        ocean_proximity=(request.form['ocean_proximity'])
        
        data=HousingData(longitude=longitude,latitude=latitude,
                         housing_median_age=housing_median_age,
                         total_rooms=total_rooms,
                         total_bedrooms=total_bedrooms,
                         population=population,
                         households=households,
                         median_income=median_income,
                         ocean_proximity=ocean_proximity)
        
        print(data.)
        housing_df=HousingData.get_housing_input_data_frame(data)
        
        housing_predictor= HousingPredictor(model_dir=MODEL_DIR)
        median_housing_value= housing_predictor.predict(x=housing_df)
        
        context={
            HOUSING_DATA_KEY:HousingData.get_housing_data_as_dict(data),
            MEDIAN_HOUSING_VALUE_KEY:median_housing_value
        }
        print(context)
        return render_template('predict.html',context=context)
    return render_template('predict.html',context=context)


if __name__=="__main__":
    app.run()
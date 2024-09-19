from flask import Flask, request
from flask import send_file ,abort,render_template
import os,sys
import pip
import json
from house.exception import HouseException
from house.logger import logging
from house.logger import get_log_data_frame
from house.config.configuration import Configuration
from house.constant import *
from house.pipeline.pipeline import Pipelines
from house.entity.housing_predictors import HousingPredictor,HousingData
from house.util.util import read_yaml_file,write_yaml_file
from matplotlib.style import context
import  pandas as pd


ROOT_DIR=os.getcwd()
LOG_FOLDER_NAME="housing_logs"
PIPELINE_FOLDER_NAME="house"
SAVED_MODEL_DIR_NAME="saved_models"
MODEL_CONFIG_FILE_PATH=os.path.join(ROOT_DIR,CONFIG_DIR,"model.yaml")
LOG_DIR=os.path.join(ROOT_DIR,LOG_FOLDER_NAME)
print(LOG_DIR)
PIPELINE_DIR=os.path.join(ROOT_DIR,PIPELINE_FOLDER_NAME)
print(PIPELINE_DIR)
MODEL_DIR=os.path.join(ROOT_DIR,SAVED_MODEL_DIR_NAME)
print(MODEL_DIR)

HOUSING_DATA_KEY="data"
MEDIAN_HOUSING_VALUE_KEY="median_housing_value"

app= Flask(__name__)

@app.route('/artifacts',defaults={'req_path':'housing'})
@app.route('/artifact/<path:req_path>')
def render_artifact_dir(req_path):
    os.makedirs("housing",exist_ok=True)
    ## joining the base and requested path
    print(f"req_path:{req_path}")
    abs_path=os.path.join(req_path)
    print(abs_path)
    #Return 404 if path doesn't exists
    if not os.path.exists(abs_path):
        return abort(404)
    
    # check if path is a file and serve
    if os.path.isfile(abs_path):
        if ".html" in abs_path:
            with open(abs_path,"r",encoding='utf-8') as file:
                content=''
                for line in file.readlines():
                    content=f"{content}{line}"
                return content
        return send_file(abs_path)
    
    #show directory contents
    files={os.path.join(abs_path,file_name):file_name for file_name in os.listdir(abs_path)
           if "artifact" in os.path.join(abs_path,file_name)}
    
    result= {"files":files,"Parent_folder":os.path.dirname(abs_path),
             "parent_label":abs_path}
    
    return render_template ('file.html',result=result)

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

@app.route('/train',methods=['GET','POST'])
def train():
    message=""
    pipeline=Pipelines(config=Configuration(current_time_stamp=get_current_time_stamp()))
    if not Pipelines.experiment.running_status:
        message="Training started"
        pipeline.start()
    else:
        message="Training is already in progress"
    context={
        "experiment":Pipelines.get_experiments_status.to_html(classes='table table-striped col-12'),
        "message":message}
    
    return render_template('train.html',context=context)
    
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
        
        data = HousingData(longitude=longitude,latitude=latitude,housing_median_age=housing_median_age,
                                  total_rooms=total_rooms,total_bedrooms=total_bedrooms,population=population,
                                  households=households,median_income=median_income,ocean_proximity=ocean_proximity)
        
        housing_df=data.get_housing_input_data_frame()
        housing_predictor= HousingPredictor(model_dir=MODEL_DIR)
        median_housing_value= housing_predictor.predict(X=housing_df)
        
        context={
            HOUSING_DATA_KEY:data.get_housing_data_as_dict(),
            MEDIAN_HOUSING_VALUE_KEY:median_housing_value
        }
        print(context)
        return render_template('predict.html',context=context)
    return render_template('predict.html',context=context)


@app.route('/saved_models',defaults={'req_path':''})
@app.route(f'/{SAVED_MODEL_DIR_NAME}/<path:req_path>')
def saved_models_dir(req_path):
    base_dir=os.path.join(os.getcwd(),SAVED_MODEL_DIR_NAME) ## this is to get the complete path of saved_models
    os.makedirs(base_dir,exist_ok=True)
     ## joining the base and request path
    abs_path=os.path.join(base_dir,req_path)
    logging.info(f"req_path:{req_path}")
    logging.info(f"req_path:{abs_path}")
    print(f"req_path:{req_path}")
    print(f"abs_path:{abs_path}")
    ## return 404 if path does not exists
    if not os.path.exists(abs_path):
        return abort(404)
    
    # check if path is a file or server
    
    if  os.path.isfile(abs_path):
        return send_file(abs_path)
    
    # show the dictionary content
    files={os.path.join(req_path,file): file for file in os.listdir(abs_path)}
    
    result={
        "files": files,
        "parent_folder":os.path.dirname(abs_path),
        "parent_label":abs_path
    }
    
    return render_template('saved_models_files.html',result=result)

@app.route('/update_model_config',methods=['POST','GET'])
def update_model_config():
    try:
        if request.methods=='POST':
            model_config=request.form['new_model_config']
            model_config=model_config.replace("'",'"')
            print(model_config)
            model_config=json.loads(model_config)
            
            write_yaml_file(file_path=MODEL_CONFIG_FILE_PATH,data=model_config)
        model_config=read_yaml_file(file_path=MODEL_CONFIG_FILE_PATH)
        return render_template('update_model.html',result={'model_config':model_config})
    except Exception as e:
        logging.exception(e)
        return str(e)
    
    
@app.route(f'/housing_logs',defaults={'req_path':''})## for the parent directory
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')## for the subfolder or file
def render_log_dir(req_path):
    os.makedirs(LOG_FOLDER_NAME,exist_ok=True)
    ## joining the base and request path
    logging.info(f"req_path:{req_path}")
    print(f"req_path:{req_path}")
    abs_path=os.path.join(LOG_FOLDER_NAME,req_path)
    logging.info(f"Requested path: {abs_path}")
    print(abs_path)
    ## return 404 if path does not exists
    if not os.path.exists(abs_path):
        return abort(404)
    
    #check if path is a file and serve
    
    if os.path.isfile(abs_path):
        log_df=get_log_data_frame(abs_path)
        context={"log":log_df.to_html(classes="table-striped",index=False)}
        return render_template('log.html',context=context)
    
    #show the directory contents
    files = {os.path.join(req_path,file): file for file in os.listdir(abs_path)}
    
    result={
        "files": files,
        "parent_folder":os.path.dirname(abs_path),
        "parent_label":abs_path
    }
    return render_template('log_files.html',result=result)

if __name__=="__main__":
    app.run()

    

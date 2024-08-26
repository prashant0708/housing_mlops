import logging 
from datetime import datetime 
import os 
import pandas as pd

LOG_DIR= "housing_logs"

CURRENT_TIME_STEMP= f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"


def get_log_file_name():
    return f"log_{CURRENT_TIME_STEMP}.log"

LOG_FILE_NAME=get_log_file_name()


os.makedirs(LOG_DIR,exist_ok=True)

LOG_FILE_PATH =os.path.join(LOG_DIR,LOG_FILE_NAME)

logging.basicConfig(
filename=LOG_FILE_PATH,
filemode="w",
format='[%(asctime)s]^;%(levelname)s^;%(lineno)d^;%(filename)s^;%(funcName)s()^;%(message)s',
level=logging.INFO
)

def get_log_dataframe(file_path):
    data=[]
    with open(file_path) as log_file:
        for line in log_file.readlines():
            data.append(line.split("^;"))
        log_df=pd.DataFrame(data)
        columns=["Time Stamp","Log level","line number","file name","Function name","message"]
        log_df.columns=columns
        log_df["log_message"] = log_df['Time Stamp'].astype(str)+":&"+log_df["message"]
        return log_df[["_log_message"]]
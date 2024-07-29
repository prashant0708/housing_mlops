import logging 
from datetime import datetime 
import os 

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
format='[%(asctime)s] %(name)s -%(levelname)s - %(message)s',
level=logging.INFO                  
)
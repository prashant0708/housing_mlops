import yaml 
from house.exception import HouseException
import os
import sys

def read_yaml_file(file_path:str)->dict:
    """
    Read the yaml file and return the content as dict
    file_path : str
    """
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
        
    except Exception as e:
        raise HouseException(e,sys) from e 
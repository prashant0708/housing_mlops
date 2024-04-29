from house.pipeline.pipeline import Pipelines
from house.exception import HouseException
from house.logger import logging
from house.component.data_ingestion import DataIngestion

def main():
    pipelines= Pipelines()
    pipelines.run_pipeline()
    
if __name__=="__main__":
    main()
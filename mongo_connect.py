from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.collection = MongoClient(os.getenv("uri"), server_api=ServerApi('1'))['db']['data']

    def insert_many_data(self, data):
        self.collection.insert_many(data.to_dict('records'))

    def insert_data(self, data):
        self.collection.insert_one(data.to_dict('records'))

    def return_data(self):
        return pd.DataFrame(self.collection.find())
    
    def drop_id(self, df):
        pass
        

   

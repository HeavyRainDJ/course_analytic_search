from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)

def get_db(db_name):
    return client[db_name]
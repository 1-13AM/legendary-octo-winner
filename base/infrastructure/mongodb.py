from loguru import logger
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
load_dotenv()

class MongoDatabaseConnector:
    # convention for private variables in Python, starting with "_"
    _instance: MongoClient | None = None
    
    def __new__(cls, *args, **kwargs) -> MongoClient:
        if cls._instance is None:
            try:
                mongo_url = os.getenv('MONGODB_CONNECTION_STRING')
                cls._instance = MongoClient(mongo_url)
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
        
        logger.info(f"Connection to MongoDB with URL successfully: {mongo_url}")
        return cls._instance

connection = MongoDatabaseConnector()
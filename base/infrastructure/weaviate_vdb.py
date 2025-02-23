import weaviate
from weaviate.client import WeaviateAsyncClient, WeaviateClient
from weaviate.classes.init import Auth
from dotenv import load_dotenv
from loguru import logger
import os
load_dotenv()

class WeaviateDatabaseConnector:
    _instance: WeaviateClient | WeaviateAsyncClient | None = None
    
    def __new__(cls, *args, **kwargs) -> WeaviateClient | WeaviateAsyncClient:
        try:
            cls._instance = weaviate.connect_to_weaviate_cloud(
                cluster_url = os.getenv('WEAVIATE_URL'),
                auth_credentials = Auth.api_key(os.getenv('WEAVIATE_API_KEY')),
                headers={'X-OpenAI-Api-Key': os.getenv('OPENAI_API_KEY')}
            )
            logger.info(cls._instance.is_ready())
        except Exception as e:
            logger.error(f"Error while connecting to Weaviate: {e}")
            
        logger.info(f"Connection to Weaviate with URL successfully: {os.getenv('WEAVIATE_URL')}")
        return cls._instance

connection = WeaviateDatabaseConnector()
            
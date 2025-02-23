from weaviate.classes.config import Property, DataType, Configure
from typing import List, Dict, Any
from ..ovm import VectorBaseModel
from ..infrastructure.weaviate_vdb import connection

class UserCodeStore(VectorBaseModel):
    
    class Settings:
        name: str= "user_code"
        properties: List[Property] = [
            Property(
                name="user_id",
                data_type=DataType.TEXT
            ),
            Property(
                name="code",
                data_type=DataType.TEXT
            ),
            Property(
                name="review",
                data_type=DataType.TEXT
            ),
            Property(
                name="date",
                data_type=DataType.DATE
            )
        ]
        description: str = "Collection containing user code"
        
        # for the time being, we will use the openai embeddings
        vectorizer_config: List[Any] = [
                            Configure.NamedVectors.text2vec_openai(
                                name="review_vector",
                                source_properties=["review"],
                                # If using `text-embedding-3` model family
                                model="text-embedding-3-small",
                            )
                        ]
    
    @classmethod
    def create_collection(cls):
        
        return connection.collections.create(
            name=cls.Settings.name,
            vectorizer_config=cls.Settings.vectorizer_config,
            description=cls.Settings.description,
            properties=cls.Settings.properties
        )
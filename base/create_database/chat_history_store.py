from weaviate.classes.config import Property, DataType, Configure
from typing import List, Dict, Any
from ..ovm import VectorBaseModel
from ..infrastructure.weaviate_vdb import connection

class ChatHistoryStore(VectorBaseModel):
    
    class Settings:
        name: str = "chat_history"
    
        properties: List[Property]=[
                        Property(
                                name="conversation_id",
                                data_type=DataType.TEXT,
                                primary=True
                        ),  
                        Property(
                                name="user_id",
                                data_type=DataType.TEXT
                        ),
                        Property(
                                name="conversation",
                                data_type=DataType.TEXT
                            ),
                        Property(
                                name="context_tags",
                                data_type=DataType.TEXT_ARRAY
                            ),
                        Property(
                                name="conversation_summary",
                                data_type=DataType.TEXT
                        ),
                        Property(
                                name="what_worked",
                                data_type=DataType.TEXT
                        ),
                        Property(
                                name="what_to_avoid",
                                data_type=DataType.TEXT
                        ),
                        Property(
                                name="user_skill_evaluation",
                                data_type=DataType.TEXT
                        ),
                        Property(
                                name="created_date",
                                data_type=DataType.DATE
                        ),
                        Property(
                                name="last_accessed",
                                data_type=DataType.DATE
                        ),
                        Property(
                                name="access_counts",
                                data_type=DataType.INT
                        ),
                        Property(
                                name="decay_factor",
                                data_type=DataType.NUMBER
                        ),
                        Property(
                                name="total_token_length",
                                data_type=DataType.INT
                        ),
                        Property(
                                name="num_interactions",
                                data_type=DataType.INT
                        )
                    ]
        description: str = "Collection containing historical chat interactions and takeaways"
        
        # for the time being, we will use the openai embeddings
        vectorizer_config: List[Any] = [
                            Configure.NamedVectors.text2vec_openai(
                                name="summary_vector",
                                source_properties=["conversation_summary"],
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

    
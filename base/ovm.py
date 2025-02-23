from .infrastructure.weaviate_vdb import connection
from pydantic import  UUID4, BaseModel, Field
from weaviate.classes.config import Configure, Property
from weaviate.collections.collection import Collection
from typing import Any, Dict, List, Type, TypeVar
from loguru import logger
from abc import ABC

T = TypeVar('T', bound='VectorBaseModel')

class VectorBaseModel(BaseModel, ABC):
    # Allow arbitrary types to resolve Pydantic schema generation issues
    # model_config = ConfigDict(
    #     arbitrary_types_allowed=True,
    #     from_attributes=True
    # )
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        
        return self.id == value.id
    
    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def upsert(cls: Type[T], data: Dict[str, Any]) -> str:
        collection_name = cls.get_collection_name()
        collection = connection.collections.get(collection_name)
        try:
            result = collection.data.insert(data)
            return result
        except Exception as e:
            logger.error(f"Failed to insert document into {collection_name}: {e}")
    
    @classmethod
    def bulk_upsert(cls: Type[T], data: List[Dict[str, Any]]) -> List[str]:
        collection_name = cls.get_collection_name()
        collection = connection.collections.get(collection_name)
        try:
            result = [collection.data.insert(d) for d in data]
            
            logger.info(f"Inserted {len(result)} documents into {collection_name}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to insert documents into {collection_name}: {e}")
            raise
    
    @classmethod
    def search(cls: Type[T], query: str | None = None, **search_kwargs) -> List[T]:
        collection_name = cls.get_collection_name()
        collection = connection.collections.get(collection_name)
        if query:
            try:
                results = collection.query.hybrid(
                    query=query,
                    **search_kwargs
                )
                return [obj.properties for obj in results.objects]
            except Exception as e:
                logger.error(f"Failed to query collection {collection_name}: {e}")
                raise
            
    def vector_search(cls: Type[T], query_embedding: List[float], **search_kwargs) -> List[T]:
        """
        Should the query_embedding be normalized?
        """
        
        collection_name = cls.get_collection_name()
        collection = connection.collections.get(collection_name)
        try:
            results = collection.query.near_vector(
                near_vector=query_embedding,
                **search_kwargs
            )
            return [obj.properties for obj in results.objects]
        except Exception as e:
            logger.error(f"Failed to query collection {collection_name}: {e}")
            raise
        
    @classmethod
    def update(
        cls: Type[T],
        uuid: str,
        update_data: Dict[str, Any]
    ):
        collection_name = cls.get_collection_name()
        collection = connection.collections.get(collection_name)
        try:
            result = collection.data.update(uuid=uuid, properties=update_data)
            return result
        except Exception as e:
            logger.error(f"Failed to update document in {collection_name}: {e}")
            raise
    
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ValueError(
                "The class should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name

    ### Create a class method that retrieves the uuid from a given instance
    @classmethod
    def get_uuid(cls: Type[T], instance: T) -> str:
        pass 
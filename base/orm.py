import uuid
from abc import ABC
from typing import Generic, Type, TypeVar

from loguru import logger
from pydantic import UUID4, BaseModel, Field
from pymongo import errors

from .infrastructure.mongodb import connection
from dotenv import load_dotenv
import os
load_dotenv()

# this operation either creates a new document or get an existing one
print(os.getenv("MONGODB_DATABASE_NAME"))
_database = connection.get_database(os.getenv("MONGODB_DATABASE_NAME"))
# generic type
T = TypeVar("T", bound="NoSQLBaseModel")

class NoSQLBaseModel(BaseModel, ABC):
    # abstract class for all tables
    # why do we need an id field here, even though the database created one for us already?
    id: UUID4 = Field(default_factory=uuid.uuid4)
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        
        return self.id == value.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    @classmethod
    def from_mongo(cls: Type[T], data: dict) -> T:
        """Convert "_id" (str object) into "id" (UUID object)."""

        if not data:
            raise ValueError("Data is empty.")

        id = data.pop("_id")

        return cls(**dict(data, id=id))
    
    def to_mongo(self: T, **kwargs) -> dict:
        """Convert "id" (UUID object) into "_id" (str object)."""
        parsed = self.model_dump(**kwargs)
        
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))
        
        for key, value in parsed.items():
            if isinstance(value, uuid.UUID):
                parsed[key] = str(value)
        return parsed

    def model_dump(self: T, **kwargs) -> dict:
        dict_ = super().model_dump(**kwargs)
        
        for key, value in dict_.items():
            if isinstance(value, uuid.UUID):
                dict_[key] = str(value)
        
        return dict_
    
    def save(self: T, **kwargs) -> T | None:
        collection = _database[self.get_collection_name()]
        try:
            collection.insert_one(self.to_mongo(**kwargs))
            
            return self
        except errors.WriteError:
            logger.exception("Failed to insert documents.")
            
            return None
    
    @classmethod
    def get_or_create(cls: Type[T], **filter_options) -> T:
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options) 
            if instance:
                return cls.from_mongo(instance)
            
            new_instance = cls(**filter_options)
            new_instance = new_instance.save()
            
            return new_instance
        except errors.OperationFailure:
            logger.exception(f"Failed to retrieve document with filter options: {filter_options}")
            # what are you raising here?    
            raise
    
    @classmethod
    def bulk_insert(cls: Type[T], documents: list[T], **kwargs) -> bool:
        collection = _database[cls.get_collection_name()]
        try:
            collection.insert_many(doc.to_mongo(**kwargs) for doc in documents)
            
            return True
        except (errors.WriteError, errors.BulkWriteError):
            logger.error(f"Failed to insert documents of type {cls.__name__}")
            
            return False
        
    @classmethod
    def find(cls: Type[T], **filter_options) -> T | None:
        collection = _database[cls.get_collection_name()]
        try:
            instance = collection.find_one(filter_options)
            if instance:
                return cls.from_mongo(instance)

            return None
        except errors.OperationFailure:
            logger.error("Failed to retrieve document")

            return None
    
    @classmethod
    def bulk_find(cls: Type[T], **filter_options) -> list[T]:
        collection = _database[cls.get_collection_name()]
        try:
            instances = collection.find(filter_options)
            return [document for instance in instances if (document := cls.from_mongo(instance)) is not None]
        except errors.OperationFailure:
            logger.error("Failed to retrieve documents")

            return []
    
    @classmethod
    def delete(cls: Type[T], **filter_options) -> bool:
        collection = _database[cls.get_collection_name()]
        try:
            collection.delete_one(filter_options)
            return True
        except errors.OperationFailure:
            logger.error("Failed to delete document")
            return False
        
    # in case you don't want to create a Settings class in every pydantic model class
    # @classmethod
    # def get_collection_name(cls: Type[T]) -> str:
    #     # NOTE: the child classes must have a variable called "name" for collection names
    #     return cls.model_fields["name"].default
    
    @classmethod
    def get_collection_name(cls: Type[T]) -> str:
        if not hasattr(cls, "Settings") or not hasattr(cls.Settings, "name"):
            raise ImproperlyConfigured(
                "Document should define an Settings configuration class with the name of the collection."
            )

        return cls.Settings.name
    
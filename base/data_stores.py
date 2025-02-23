from socketserver import StreamRequestHandler
from .ovm import VectorBaseModel
from weaviate.classes.config import Property, DataType
from typing import List
import datetime
class ChatHistoryChunk(VectorBaseModel):
    
    user_id: str
    conversation_id: str
    conversation: str
    context_tags: List[str]
    conversation_summary: str
    what_worked: str
    what_to_avoid: str
    user_skill_evaluation: str
    created_date: datetime.datetime
    last_accessed: datetime.datetime
    access_counts: int
    decay_factor: float
    
    class Settings:
        name = "chat_history"
    
class UserCode(VectorBaseModel):
    
    user_id: str
    code: str
    review: str
    date: datetime.datetime
    
    class Settings:
        name = "user_code"
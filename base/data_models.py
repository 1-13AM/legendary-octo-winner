from .orm import NoSQLBaseModel
from typing import List

class User(NoSQLBaseModel):
    first_name: str
    last_name: str
    dob: str
    grade: str
    evaluation_comments: str
    
    class Settings:
        name: str = "users"
    
class UserChatHistory(NoSQLBaseModel):
    user_id: str
    conversation: dict
    context_tags: List[str]
    conversation_summary: str
    what_worked: str
    what_to_avoid: str
    user_skill_evaluation: str
    date: str
    
    class Settings:
        name: str = "user_chat_history"
        
class UserCode(NoSQLBaseModel):
    user_id: str
    code: str
    review: str
    
    class Settings:
        name: str = "user_code"
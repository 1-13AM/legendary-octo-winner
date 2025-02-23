from .chat_history_store import ChatHistoryStore
from .user_code_store import UserCodeStore

if __name__ == "__main__":
    ChatHistoryStore.create_collection()
    UserCodeStore.create_collection()
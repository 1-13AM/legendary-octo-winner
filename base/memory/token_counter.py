import openai
# import transformers
import tiktoken
from loguru import logger

class TokenCounter:
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        # load the huggingface tokenizer
        # if not model.startswith('text-embedding'):
        #     self.tokenizer = transformers.AutoTokenizer.from_pretrained(model)
    
    def count_tokens(self, text: str) -> int:
        # OpenAI models
        if self.model.startswith('text-embedding'):
            try:
                encoding = tiktoken.encoding_for_model(self.model)
                return len(encoding.encode(text))
            except Exception as e:
                logger.error(e)
                logger.error(f"Failed to count tokens for text: {text[:min(100, len(text))]}. Fall back to word count")
                return len(text.split())
        
        # Imply that the model is a HuggingFace model
        # else:
        #     try:
        #         return len(self.tokenizer.encode(text))
        #     except Exception:
        #         logger.error(f"Failed to count tokens for text: {text[:min(100, len(text))]}. Fall back to word count")
        #         return len(text.split())
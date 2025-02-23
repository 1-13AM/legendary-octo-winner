### Create a class that handles all llm-related operations on memory
from openai import OpenAI
from typing import Dict
from dotenv import load_dotenv
import os
load_dotenv()

class MemoryWorkflowOpenAI:
    
    def __init__(self, model_name='gpt-4o-mini-2024-07-18'):
        
        self.model_name = model_name
    
        if not os.getenv("OPENAI_API_KEY"):
            raise Exception("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI()
        self.client.api_key = os.getenv("OPENAI_API_KEY")
        
    def generate_response(self, prompt: str, **generation_kwargs) -> str:
        
        print(prompt)
        print('=' * 80)
        print(generation_kwargs)
        
        if generation_kwargs.get('response_format') is not None:
            response = self.client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a chatbot that is good at summarizing conversations."},
                    {"role": "user", "content": prompt}
                ],
                **generation_kwargs
            )
            return dict(response.choices[0].message.parsed)
        else:  
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a chatbot that is good at summarizing conversations."},
                    {"role": "user", "content": prompt}
                ],
                **generation_kwargs
            )
            return response.choices[0].message.content

    def extract_context_tags(self, text: str) -> str:
        ### needs to be optimized ###
        CONCEPT_EXTRACTION_PROMPT = f"Extract key context tags from the following text in a concise, context-specific manner. Include only highly relevant and specific concepts.\n{text}"
        
        return self.generate_response(CONCEPT_EXTRACTION_PROMPT)

    def extract_working_strategies(self, text: str) -> str:
        ### needs to be optimized ###
        STRATEGY_EXTRACTION_PROMPT = f"Extract key working strategies from the following text in a concise, context-specific manner. Include only highly relevant and specific concepts.\n{text}"
        
        return self.generate_response(STRATEGY_EXTRACTION_PROMPT)
    
    def extract_what_to_avoid(self, text: str) -> str:
        ### needs to be optimized ###
        AVOID_EXTRACTION_PROMPT = f"Extract key things to avoid from the following text in a concise, context-specific manner. Include only highly relevant and specific concepts.\n{text}"
        
        return self.generate_response(AVOID_EXTRACTION_PROMPT)
    
    def extract_user_skill_evaluation(self, text: str) -> str:
        ### needs to be optimized ###
        SKILL_EVALUATION_PROMPT = f"Extract user's skill evaluation from the following text in a concise, context-specific manner. Include only highly relevant and specific concepts.\n{text}"
        
        return self.generate_response(SKILL_EVALUATION_PROMPT)
    
    def extract_summary(self, text: str) -> str:
        ### needs to be optimized ###
        SUMMARY_EXTRACTION_PROMPT = f"Extract summary from the following text in a concise, context-specific manner. Include only highly relevant and specific concepts.\n{text}"
        
        return self.generate_response(SUMMARY_EXTRACTION_PROMPT)
    
    def extract_all(self, conversation: str) -> Dict[str, str]:
        
        from ..prompts.reflection_prompt import REFLECTION_PROMPT_TEMPLATE, ReflectionResponse
        
        # context_tags = self.extract_context_tags(text)
        # working_strategies = self.extract_working_strategies(text)
        # what_to_avoid = self.extract_what_to_avoid(text)
        # user_skill_evaluation = self.extract_user_skill_evaluation(text)
        # summary = self.extract_summary(text)
        return self.generate_response(prompt=REFLECTION_PROMPT_TEMPLATE.format(conversation=conversation), response_format=ReflectionResponse)
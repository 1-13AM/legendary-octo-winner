from ..prompts.explainer_system_prompt import SYSTEM_PROMPT_TEMPLATE
from ..prompts.user_info_prompt import USER_INFO_PROMPT_TEMPLATE
from ..prompts.query_concept_extraction_prompt import QUERY_CONCEPT_EXTRACTION_PROMPT_TEMPLATE, QueryConceptResponse
from ..memory.memory_store import WeaviateMemoryStore
from weaviate.classes.query import Sort
from typing import Dict, List
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()

RELEVANT_INTERACTION_PROMPT = """
Here are some interactions between you and the user that may be relevant to the user's request:
{related_interactions}
"""

PAST_INTERACTION_PROMPT = """
Here is the latest interaction beteween you and the user:
{past_interactions}
"""

# final_prompt = """
# {system_prompt}
# {user_info}
# {related_interactions}
# {past_interactions}
# Here is the user's request:
# {query}
# Your response:

# """

# Exclude user_info here, we need further consideration on this
FINAL_PROMPT = """
{related_interactions}
{past_interactions}
Now the user ask you this:
{query}
Your response:
"""

class ConversationManager:
    def __init__(self, embedding_model: str = "text-embedding-3-small", llm: str = "gpt-4o-mini-2024-07-18", embedding_dim: int = 1536):
        self.memory_store = WeaviateMemoryStore()
        self.embedding_model = embedding_model
        self.embedding_dim = embedding_dim
        self.llm = llm
        
        if not os.getenv("OPENAI_API_KEY"):
            raise Exception("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI()
        self.client.api_key = os.getenv("OPENAI_API_KEY")
        
    def _embed_query(self, query: str) -> List[float]:
        try:
            # Generate embedding using OpenAI's API
            response = self.client.embeddings.create(
                input=[query],  # Input must be a list
                model=self.embedding_model
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            return embedding
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return a default zero vector or raise an exception
            return [0.0] * self.embedding_dim  # Default size for text-embedding-ada-002
    
    def _generate_response(self, user_prompt: str, system_prompt: str = None, **generation_kwargs) -> str:
        if system_prompt is None:
            system_prompt = "You are a helpful chatbot"
        if generation_kwargs.get('response_format') is not None:
            response = self.client.beta.chat.completions.parse(
                model=self.llm,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **generation_kwargs
            )
            return dict(response.choices[0].message.parsed)
        else:
            response = self.client.chat.completions.create(
                model=self.llm,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                **generation_kwargs
            )
            return response.choices[0].message.content
    
    def _extract_concepts(self, query: str) -> List[str]:
        prompt = QUERY_CONCEPT_EXTRACTION_PROMPT_TEMPLATE.format(query=query)
        response = self._generate_response(user_prompt=prompt, response_format=QueryConceptResponse)
        concepts = response.get("keywords", [])
        return concepts
    
    def _retrieve_related_interactions(self, query: str) -> List[Dict[str, str]]:
        query_embedding = self._embed_query(query)
        query_concepts = self._extract_concepts(query)
        return self.memory_store.retrieve_relevant_chunks(query_embedding, query_concepts, similarity_threshold=0.125)
        
    def _add_related_interaction(self, query: str) -> str:
        related_interactions: List[Dict[str, str]] = self._retrieve_related_interactions(query)
        str_related_interactions = ""
        for idx, interaction in enumerate(related_interactions):
            str_related_interactions += f"Related interaction #{idx + 1}: \n"
            str_related_interactions += interaction.get('conversation')
            str_related_interactions += "\n"
        return RELEVANT_INTERACTION_PROMPT.format(related_interactions=str_related_interactions)
        
    def _get_past_interactions(self) -> Dict[str, str]:
        return self.memory_store.retrieve_k_latest_chunks()
    
    def _add_past_interaction(self) -> str:
        past_interactions: Dict[str, str] = self._get_past_interactions()

        return PAST_INTERACTION_PROMPT.format(past_interactions="\n".join(interaction['conversation'] for interaction in past_interactions))
        
    
    def _add_user_info(self, first_name: str, evaluation_comments: str, rules_for_responses: List[str]) -> str:

        return USER_INFO_PROMPT_TEMPLATE.format(first_name, evaluation_comments, "\n".join("- " + rule for rule in rules_for_responses))
    
    def _add_system_prompt(self) -> str:
        
        return SYSTEM_PROMPT_TEMPLATE
    
    def compile_prompt(cls, query: str):
        related_interactions = cls._add_related_interaction(query)
        past_interactions = cls._add_past_interaction()
        # user_info = cls._add_user_info()
        system_prompt = cls._add_system_prompt()
        
        return FINAL_PROMPT.format(
                                # system_prompt=system_prompt, 
                                #    user_info=user_info, 
                                   related_interactions=related_interactions, 
                                   past_interactions=past_interactions, 
                                   query=query)
    
    def respond(self, query: str):
        user_prompt = self.compile_prompt(query)
        print(user_prompt)
        response = self._generate_response(user_prompt=user_prompt, system_prompt=SYSTEM_PROMPT_TEMPLATE)
        return response
        
         
        
        
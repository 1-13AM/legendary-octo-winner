import openai
from dotenv import load_dotenv
import os
from ..infrastructure.weaviate_vdb import connection
from ..prompts.rule_extraction_prompt import RULE_EXTRACTION_PROMPT_TEMPLATE, RuleExtractionResponse
load_dotenv()

class UserInfoUpdater:
    def __init__(self, model_name='gpt-4o-mini-2024-07-18', **generation_kwargs):
        self.model_name = model_name
        self.generation_kwargs = generation_kwargs
        # get chat history
        self.weaviate_memory_store = connection.collections.get("chat_history")
    
    def _query_chat_history(self,
                            user_id: str,
                            start_time: datetime,
                            end_time: datetime) -> List[Dict[str, Any]]:
        filter_conditions = {
            "operator": "And",
            "operands": [
                {
                    "path": ["yourDateProperty"],
                    "operator": "GreaterThanEqual",
                    "valueDate": start_time,
                },
                {
                    "path": ["yourDateProperty"],
                    "operator": "LessThanEqual",
                    "valueDate": end_time,
                },
                ]
            }
        
        # Perform the query
        # this needs to be reviewed
        result = self.weaviate_memory_store.query.get(
            "YourClassName",  # Replace with the class name in your schema
            ["property1", "property2", "yourDateProperty"]  # Properties you want to retrieve
        ).with_where(filter_conditions).do()
        
    def extract_rules_for_responses(self, what_worked: List[str], what_to_avoid: List[str]) -> List[str]:
        try: 
            prompt = RULE_EXTRACTION_PROMPT_TEMPLATE.format(what_worked=what_worked, what_to_avoid=what_to_avoid)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                prompt=prompt,
                response_format=RuleExtractionResponse,
                **self.generation_kwargs
            )
            
            return response.choices[0].message.parsed
        
        except Exception as e:
            print(f"Error extracting rules: {e}")
            return []
    
    def extract_evaluation_comments(self,
                                    user_skill_evaluation: List[str],
                                    previous_review: str = None) -> str:
        
        from ..prompts.user_level_prompt import USER_LEVEL_PROMPT_TEMPLATE, UserLevelResponse
        
        try:
            prompt = USER_LEVEL_PROMPT_TEMPLATE.format(user_skill_evaluation=user_skill_evaluation, previous_review=previous_review)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                prompt=prompt,
                response_format=UserLevelResponse,
                **self.generation_kwargs
            )
            
            return response.choices[0].message.parsed
        
        except Exception as e:
            print(f"Error extracting evaluation comments: {e}")
            return ""
    
    def update_user_info_for_time_range(self,
                                        user_id: str,
                                        start_time: Optional[datetime] = None,
                                        end_time: Optional[datetime] = None,
                                        time_window: timedelta = timedelta(days=0.5)) -> Dict[str, Any]:
        
            
        # Set default time range if not provided
        end_time = end_time or datetime.now()
        start_time = start_time or (end_time - time_window)

        # Retrieve chat history for the time range
        chat_history = self._query_chat_history(user_id, start_time, end_time)

        # Aggregate insights from chat history
        what_worked = []
        what_to_avoid = []
        user_skill_evaluation = []
        previous_reviews = []

        for entry in chat_history:
            what_worked.extend(entry.get('what_worked', []))
            what_to_avoid.extend(entry.get('what_to_avoid', []))
            user_skill_evaluation.extend(entry.get('user_skill_evaluation', []))
            previous_reviews.append(entry.get('user_skill_evaluation', ''))
        
        # Extract rules and evaluation
        rules_for_responses = self.extract_rules_for_responses(
            what_worked=list(set(what_worked)),
            what_to_avoid=list(set(what_to_avoid))
        )
        
        # evaluation_comments = self.extract_evaluation_comments(
        #     user_skill_evaluation=list(set(user_skill_evaluation)),
        #     previous_review=' '.join(previous_reviews)
        # )
        
        
        
        
        

from pydantic import BaseModel, Field
QUERY_CONCEPT_EXTRACTION_PROMPT_TEMPLATE = """
You are an assistant tasked with identifying 2-4 keywords that summarize the essence of a conversation to help classify it and identify similar future conversations. Follow these guidelines:

1. Extract only 2-4 relevant keywords that are concise and informative.
2. Ensure the keywords are standard, consistent, and not offset by any extra characters or variations.
3. Always provide the keywords in English, regardless of the language used in the conversation.
4. Focus on technical or thematic terms that best represent the topic.
5. Prioritize programming concepts, algorithms, or relevant libraries since most queries will be about coding. For example:
"debugging"
"dynamic_programming"
"if_else_statement"

You should strictly respond in the given structure.
Input:
{query}
"""

class QueryConceptResponse(BaseModel):
    keywords: list[str] = Field(...,description="List of key concepts extracted from the conversation.")
    
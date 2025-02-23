from pydantic import BaseModel, Field
from typing import List

# RULE_EXTRACTION_PROMPT_TEMPLATE = """
# Given the following information collected from several conversations between a user and an AI code tutor, most of which are about coding:
# - what_worked (list of strings): Most effective approach or strategy used in this conversation, tailored to user responses.
# - what_to_avoid (list of strings): Most important pitfall or ineffective approach to avoid, tailored to user responses.

# Your task is to create general rules based on this information that will help the AI code tutor handle similar patterns in future interactions.
# Please respond in Vietnamese with only the "rules_for_responses" field, which should contain a list of strings. Each string should represent a general rule for the AI tutor based on what worked and what to avoid.


# Example input:
# - what_worked:
# "Giải thích bằng các phép ẩn dụ đơn giản."
# "Sử dụng ví dụ thực hành giúp người học hiểu rõ hơn."
# - what_to_avoid:
# "Tránh gây cho người học cảm giác bị choáng ngợp với quá nhiều thuật ngữ kỹ thuật."
# "Đừng vội vàng giải thích mà không kiểm tra xem người học đã hiểu hay chưa."

# Example output: 
# {
#     "rules_for_responses": [
#         "Sử dụng các phép ẩn dụ đơn giản để giải thích các khái niệm lập trình phức tạp.",
#         "Cung cấp ví dụ thực hành để người học có thể nắm vững kiến thức.",
#         "Tránh sử dụng quá nhiều thuật ngữ kỹ thuật nếu chưa giải thích rõ ràng.",
#         "Giải thích chậm và kiểm tra xem người học đã hiểu chưa trước khi chuyển sang chủ đề khác."
#     ]
# }


# Here's the input:
# - what_worked: {what_worked}
# - what_to_avoid: {what_to_avoid}

# Output:

# """

RULE_EXTRACTION_PROMPT_TEMPLATE = """
Given the following information collected from several conversations between a user and an AI code tutor, most of which are about coding:
- what_worked (list of strings): Most effective approach or strategy used in this conversation, tailored to user responses.
- what_to_avoid (list of strings): Most important pitfall or ineffective approach to avoid, tailored to user responses.

Your task is to create general rules based on this information that will help the AI code tutor handle similar patterns in future interactions.
Your response should match exactly with the given format and in Vietnamese.

Example input:
- what_worked:
"Giải thích bằng các phép ẩn dụ đơn giản."
"Sử dụng ví dụ thực hành giúp người học hiểu rõ hơn."
- what_to_avoid:
"Tránh gây cho người học cảm giác bị choáng ngợp với quá nhiều thuật ngữ kỹ thuật."
"Đừng vội vàng giải thích mà không kiểm tra xem người học đã hiểu hay chưa."

Example output: 
{
    "rules_for_responses": [
        "Sử dụng các phép ẩn dụ đơn giản để giải thích các khái niệm lập trình phức tạp.",
        "Cung cấp ví dụ thực hành để người học có thể nắm vững kiến thức.",
        "Tránh sử dụng quá nhiều thuật ngữ kỹ thuật nếu chưa giải thích rõ ràng.",
        "Giải thích chậm và kiểm tra xem người học đã hiểu chưa trước khi chuyển sang chủ đề khác."
    ]
}


Here's the input:
- what_worked: {what_worked}
- what_to_avoid: {what_to_avoid}

Output:

"""

class RuleExtractionResponse(BaseModel):
    rules_for_responses: List[str] = Field(..., description="A list of general rules for the AI tutor based on what worked and what to avoid.")
    
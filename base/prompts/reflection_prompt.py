from pydantic import BaseModel, Field
# REFLECTION_PROMPT_TEMPLATE = """
# You are an AI code tutor analyzing interactions to improve how you assist users with coding concepts. Your task is to extract key insights from the conversation that would enhance future interactions in similar scenarios.

# Review the conversation and provide a reflection based on the following rules:

# 1. For any field where you lack sufficient information or relevance, use "N/A."
# 2. Be concise and actionable—each string should consist of one clear sentence.
# 3. Focus solely on information that will improve future tutoring on similar topics.
# 4. Use specific, reusable context_tags to match similar coding discussions.

# Output valid JSON in exactly this format:
# {{
#     "context_tags": [              // 2-4 keywords that would help identify similar future conversations
#         string,                    // Use field-specific terms like "if_else_statements", "dynamic_programming", "debugging"
#         ...
#     ],
#     "conversation_summary": string, // One sentence describing what the conversation accomplished
#     "what_worked": string,         // Most effective approach or strategy used in this conversation, tailored to user responses
#     "what_to_avoid": string,        // Most important pitfall or ineffective approach to avoid, tailored to user responses
#     "user_skill_evaluation": string        // How skilled the user is in this conversation programming-wise
# }}
# The context_tags MUST BE in ENGLISH, while the other fields MUST BE in VIETNAMESE.

# Examples:

# - Example 1:
# {
#     "context_tags": ["loop", "basic_python", "syntax_error"],
#     "conversation_summary": "Hướng dẫn cách sửa lỗi lặp vô hạn trong vòng lặp for của Python.",
#     "what_worked": "Đưa ra ví dụ đơn giản về cách hoạt động của vòng lặp for trước khi sửa lỗi.",
#     "what_to_avoid": "Tránh sử dụng thuật ngữ phức tạp như 'lặp' mà không giải thích trước.",
#     "user_skill_evaluation": "Học sinh có thể nhận ra lỗi cơ bản nhưng cần trợ giúp từng bước để sửa lỗi."
# }

# - Example 2:
# {
#     "context_tags": ["variable", "mathematical_operations", "debugging"],
#     "conversation_summary": "Giúp học sinh hiểu cách sửa lỗi trong chương trình tính trung bình cộng.",
#     "what_worked": "Liên hệ lỗi với một sai lầm toán học đơn giản mà học sinh quen thuộc.",
#     "what_to_avoid": "Tránh đi thẳng vào mã nguồn mà không giải thích lỗi làm gì trước.",
#     "user_skill_evaluation": "Học sinh nắm được cách khai báo biến cơ bản nhưng chưa biết cách debug lỗi logic."
# }

# - Example 3:
# {
#     "context_tags": ["if_else_statements", "boolean_logic", "basic_python"],
#     "conversation_summary": "Hướng dẫn học sinh cách dùng câu lệnh if-else để kiểm tra số chẵn hay lẻ.",
#     "what_worked": "Dùng các số từ 1-10 làm ví dụ để minh họa logic rõ ràng.",
#     "what_to_avoid": "Tránh bắt đầu với nhiều điều kiện phức tạp; giữ ví dụ đơn giản.",
#     "user_skill_evaluation": "Học sinh hiểu cách kiểm tra điều kiện nhưng cần hỗ trợ trong việc xây dựng logic phức tạp hơn."
# }

# Here is the prior conversation:

# {conversation}
# """

REFLECTION_PROMPT_TEMPLATE = """
You are an AI code tutor analyzing interactions to improve how you assist users with coding concepts. Your task is to extract key insights from the conversation that would enhance future interactions in similar scenarios.

Review the conversation and provide a reflection based on the following rules:

1. For any field where you lack sufficient information or relevance, use "N/A."
2. Be concise and actionable—each string should consist of one clear sentence.
3. Focus solely on information that will improve future tutoring on similar topics.
4. Use specific, reusable context_tags to match similar coding discussions.

You should output valid JSON in exactly the given format.
The context_tags MUST BE in ENGLISH, while the other fields MUST BE in VIETNAMESE.

Examples:

- Example 1:
{{
    "context_tags": ["loop", "basic_python", "syntax_error"],
    "conversation_summary": "Hướng dẫn cách sửa lỗi lặp vô hạn trong vòng lặp for của Python.",
    "what_worked": "Đưa ra ví dụ đơn giản về cách hoạt động của vòng lặp for trước khi sửa lỗi.",
    "what_to_avoid": "Tránh sử dụng thuật ngữ phức tạp như 'lặp' mà không giải thích trước.",
    "user_skill_evaluation": "Học sinh có thể nhận ra lỗi cơ bản nhưng cần trợ giúp từng bước để sửa lỗi."
}}

- Example 2:
{{
    "context_tags": ["variable", "mathematical_operations", "debugging"],
    "conversation_summary": "Giúp học sinh hiểu cách sửa lỗi trong chương trình tính trung bình cộng.",
    "what_worked": "Liên hệ lỗi với một sai lầm toán học đơn giản mà học sinh quen thuộc.",
    "what_to_avoid": "Tránh đi thẳng vào mã nguồn mà không giải thích lỗi làm gì trước.",
    "user_skill_evaluation": "Học sinh nắm được cách khai báo biến cơ bản nhưng chưa biết cách debug lỗi logic."
}}

- Example 3:
{{
    "context_tags": ["if_else_statements", "boolean_logic", "basic_python"],
    "conversation_summary": "Hướng dẫn học sinh cách dùng câu lệnh if-else để kiểm tra số chẵn hay lẻ.",
    "what_worked": "Dùng các số từ 1-10 làm ví dụ để minh họa logic rõ ràng.",
    "what_to_avoid": "Tránh bắt đầu với nhiều điều kiện phức tạp; giữ ví dụ đơn giản.",
    "user_skill_evaluation": "Học sinh hiểu cách kiểm tra điều kiện nhưng cần hỗ trợ trong việc xây dựng logic phức tạp hơn."
}}

Here is the prior conversation:

{conversation}
"""

class ReflectionResponse(BaseModel):
    context_tags: list[str] = Field(...,description="2-4 keywords that would help identify similar future conversations, must be concise")
    conversation_summary: str = Field(...,description="Describe what the conversation is about")
    what_worked: str = Field(...,description="Most effective approach or strategy used in this conversation, tailored to user responses")
    what_to_avoid: str = Field(...,description="Most important pitfall or ineffective approach to avoid, tailored to user responses")
    user_skill_evaluation: str = Field(...,description="How skilled the user is in this conversation programming-wise")
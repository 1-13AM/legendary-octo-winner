USER_INFO_PROMPT_TEMPLATE = """
Your response should base on the following user information:
* user_name (string): {first_name}
* evaluation_comments (string): {evaluation_comments}
* What the user prefers you to respond: 
{rules_for_responses}
"""

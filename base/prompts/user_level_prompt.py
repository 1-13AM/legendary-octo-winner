from pydantic import BaseModel, Field
# USER_LEVEL_PROMPT_TEMPLATE = """
# Given the following information:

# user_skill_evaluation (list of strings): A detailed evaluation of the user's coding skills on various aspects, such as understanding, problem-solving, and technical skills.
# previous_review (string): A brief review of the user's previous interactions and performance.
# Your task is to write a comprehensive and detailed review on the user's coding skills. This review will help guide another AI code tutor in assisting the user in future interactions.

# Please RESPOND IN VIETNAMESE with a thorough review that includes:

# Overall Evaluation: A detailed assessment of the user's current coding abilities across different areas.
# Strengths: Highlight the user's strengths, specifying which areas they excel in and the reasons why.
# Areas for Improvement: Identify the areas where the user struggles or requires further development, providing specific details.
# The review should be as detailed as possible, considering each aspect of the user's performance and progress.

# Example input:
# - user_skill_evaluation:
# "The user has a good grasp of basic programming concepts, including variables, loops, and conditionals, and can apply them to simple problems."
# "However, they struggle with understanding object-oriented programming (OOP) principles and often confuse concepts like inheritance and polymorphism."
# "The user demonstrates an intermediate level of proficiency with data structures but finds algorithmic problems, especially related to sorting and searching, challenging."
# "Debugging is another area where the user needs improvement. They tend to miss small mistakes or overlook error handling."
# - previous_review: "The user shows a basic understanding of programming and is comfortable with fundamental concepts. They need more practice with object-oriented concepts and algorithmic problem-solving."

# Example output:
# {
#     "overall_evaluation": "Người học có nền tảng vững chắc về các khái niệm lập trình cơ bản, có thể áp dụng chúng vào các bài toán đơn giản. Tuy nhiên, người học gặp khó khăn khi đối mặt với các vấn đề phức tạp hơn, đặc biệt là khi làm việc với lập trình hướng đối tượng và giải quyết các bài toán thuật toán.",
#     "strengths": "Người học có khả năng hiểu và áp dụng các khái niệm cơ bản về lập trình như biến, vòng lặp và câu lệnh điều kiện một cách hiệu quả. Họ cũng đã hiểu và sử dụng được các cấu trúc dữ liệu cơ bản.",
#     "areas_for_improvement": "Người học gặp khó khăn trong việc hiểu các nguyên lý lập trình hướng đối tượng (OOP), đặc biệt là khi phân biệt giữa kế thừa và đa hình. Thuật toán sắp xếp và tìm kiếm là một thách thức đối với người học, và họ cũng gặp phải vấn đề khi gỡ lỗi mã."
# }

# Here's the input:
# - user_skill_evaluation: {user_skill_evaluation}
# - previous_review: {previous_review}

# Output:

# """

USER_LEVEL_PROMPT_TEMPLATE = """
Given the following information:

user_skill_evaluation (list of strings): A detailed evaluation of the user's coding skills on various aspects, such as understanding, problem-solving, and technical skills.
previous_review (string): A brief review of the user's previous interactions and performance.
Your task is to write a comprehensive and detailed review on the user's coding skills. This review will help guide another AI code tutor in assisting the user in future interactions.

Please RESPOND IN VIETNAMESE with a thorough review that includes:

Overall Evaluation: A detailed assessment of the user's current coding abilities across different areas.
Strengths: Highlight the user's strengths, specifying which areas they excel in and the reasons why.
Areas for Improvement: Identify the areas where the user struggles or requires further development, providing specific details.
The review should be as detailed as possible, considering each aspect of the user's performance and progress.

Your response should strictly match the given format.

Example input:
- user_skill_evaluation:
"The user has a good grasp of basic programming concepts, including variables, loops, and conditionals, and can apply them to simple problems."
"However, they struggle with understanding object-oriented programming (OOP) principles and often confuse concepts like inheritance and polymorphism."
"The user demonstrates an intermediate level of proficiency with data structures but finds algorithmic problems, especially related to sorting and searching, challenging."
"Debugging is another area where the user needs improvement. They tend to miss small mistakes or overlook error handling."
- previous_review: "The user shows a basic understanding of programming and is comfortable with fundamental concepts. They need more practice with object-oriented concepts and algorithmic problem-solving."

Example output:
{
    "overall_evaluation": "Người học có nền tảng vững chắc về các khái niệm lập trình cơ bản, có thể áp dụng chúng vào các bài toán đơn giản. Tuy nhiên, người học gặp khó khăn khi đối mặt với các vấn đề phức tạp hơn, đặc biệt là khi làm việc với lập trình hướng đối tượng và giải quyết các bài toán thuật toán.",
    "strengths": "Người học có khả năng hiểu và áp dụng các khái niệm cơ bản về lập trình như biến, vòng lặp và câu lệnh điều kiện một cách hiệu quả. Họ cũng đã hiểu và sử dụng được các cấu trúc dữ liệu cơ bản.",
    "areas_for_improvement": "Người học gặp khó khăn trong việc hiểu các nguyên lý lập trình hướng đối tượng (OOP), đặc biệt là khi phân biệt giữa kế thừa và đa hình. Thuật toán sắp xếp và tìm kiếm là một thách thức đối với người học, và họ cũng gặp phải vấn đề khi gỡ lỗi mã."
}

Here's the input:
- user_skill_evaluation: {user_skill_evaluation}
- previous_review: {previous_review}

Output:

"""

class UserLevelResponse(BaseModel):
    overall_evaluation: str = Field(...,description="A detailed assessment of the user's current coding abilities across different areas.")
    strengths: str = Field(...,description="Highlight the user's strengths, specifying which areas they excel in and the reasons why.")
    areas_for_improvement: str = Field(...,description="Identify the areas where the user struggles or requires further development, providing specific details.")

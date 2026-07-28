from langchain_ollama import ChatOllama
from utils.code_utils import clean_code_output, is_valid_python

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def review_code(code, max_retries=3):

    prompt = f"""
You are a senior Python reviewer.

Review this code.

Rules:
- If the code is good, return it unchanged.
- If there are small improvements, apply them.
- Do not change the functionality.
- Return ONLY Python code.
- DO NOT use markdown.
- DO NOT use triple backticks.

Code:
{code}
"""

    for attempt in range(1, max_retries + 1):
        response = llm.invoke(prompt)
        reviewed = clean_code_output(response.content)

        if reviewed and is_valid_python(reviewed):
            return reviewed

        print(f"Reviewer attempt {attempt}: invalid Python returned. Retrying...")

    # Fallback: if the reviewer keeps failing, just keep the original code
    print("⚠️ Reviewer failed to return valid code. Keeping original.")
    return code
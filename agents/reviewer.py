from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

def review_code(code):

    prompt = f"""
You are a senior Python reviewer.

Review this code.

Rules:
- If the code is good, return it unchanged.
- If there are small improvements, apply them.
- Do not change the functionality.
- Return ONLY Python code.

Code:
{code}
"""

    response = llm.invoke(prompt)

    return response.content
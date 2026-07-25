from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

def generate_code(task):

    prompt = f"""
You are an expert Python programmer.

Generate ONLY executable Python code.

Rules:
- Return only Python code.
- No markdown.
- No explanations.
- No triple backticks.

Task:
{task}
"""

    response = llm.invoke(prompt)

    return response.content
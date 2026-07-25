from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def fix_code(code, error):

    prompt = f"""
You are an expert Python programmer.

The following code has an error.

Code:
{code}

Error:
{error}

Return ONLY the corrected Python code.
"""

    response = llm.invoke(prompt)

    return response.content

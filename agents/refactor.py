from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def refactor_code(code):

    prompt = f"""
You are a Senior Software Engineer.

Refactor the following code.

Requirements:
- Improve readability.
- Improve naming.
- Remove duplicate code.
- Improve performance.
- Follow best practices.
- Keep the same functionality.

Return ONLY the refactored code.

Code:

{code}
"""

    response = llm.invoke(prompt)

    code = (
        response.content
        .replace("```python", "")
        .replace("```", "")
        .strip()
    )

    return code
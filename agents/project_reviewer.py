from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def review_project(codebase):

    prompt = f"""
You are a Senior Software Engineer.

Review this complete software project.

Give:

1. Architecture Review
2. Code Quality
3. Performance
4. Security
5. Best Practices
6. Folder Structure
7. Bugs
8. Improvements

Finally give an overall rating out of 10.

Project:

{codebase}
"""

    response = llm.invoke(prompt)

    return response.content
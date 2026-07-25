from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

def plan(user_input):

    prompt = f"""
You are an AI Planner.

Your job is to classify the user's request.

Choose ONLY ONE of these actions:

READ
CREATE
RUN
CHAT

Examples:
User: read hello.py
READ

User: create calculator.py
CREATE

User: run test.py
RUN

User: explain python
CHAT

User Request:
{user_input}

Return ONLY one word.
"""

    response = llm.invoke(prompt)

    return response.content.strip().upper()
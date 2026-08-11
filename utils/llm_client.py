from langchain_ollama import ChatOllama


# Local Ollama LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)
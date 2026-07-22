from langchain_ollama import ChatOllama
from tools.file_reader import read_file
from tools.writer import write_file

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

print("=" * 50)
print("🤖 Agentic AI Coding Assistant")
print("Type 'exit' to quit")
print("=" * 50)

while True:

    user = input("\nYou: ")

    if user.lower() == "exit":
        break

    # Read file
    if user.startswith("read "):
        filename = user.replace("read ", "")
        print(read_file(filename))
        continue

    # Create file
    if user.startswith("create "):

        filename = user.replace("create ", "")

        print("What should I write in the file?")
        content = input("Content: ")

        result = write_file(filename, content)

        print(result)

        continue

    # Chat with AI
    response = llm.invoke(user)

    print("\nAgent:")
    print(response.content)
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from tools.file_reader import read_file
from tools.writer import write_file
from tools.executor import run_python

from agents.planner import plan
from agents.coder import generate_code
from agents.reviewer import review_code
from agents.debugger import fix_code

from memory.chat_memory import (
    save_memory,
    get_memory,
    clear_memory,
)

from rag.project_reader import read_project


# -----------------------------
# LLM
# -----------------------------
llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


# -----------------------------
# Banner
# -----------------------------
print("=" * 50)
print("🤖 Agentic AI Coding Assistant")
print("=" * 50)
print("Commands:")
print("read <filename>")
print("create <filename> <task>")
print("run <filename>")
print("memory")
print("clear")
print("project")
print("exit")
print("=" * 50)


# -----------------------------
# Main Loop
# -----------------------------
while True:

    user = input("\nYou: ").strip()

    # -----------------------------
    # Exit
    # -----------------------------
    if user.lower() == "exit":
        print("Goodbye!")
        break

    # -----------------------------
    # Show Memory
    # -----------------------------
    if user.lower() == "memory":

        print("\n📚 Conversation History:\n")

        history = get_memory()

        if len(history) == 0:
            print("No conversation history.")

        else:
            for chat in history:
                print(f"You : {chat['user']}")
                print(f"AI  : {chat['assistant']}")
                print("-" * 50)

        continue

    # -----------------------------
    # Clear Memory
    # -----------------------------
    if user.lower() == "clear":

        clear_memory()

        print("✅ Memory cleared.")

        continue

    # -----------------------------
    # Project RAG
    # -----------------------------
    if user.lower() == "project":

        print("📂 Reading project...\n")

        codebase = read_project()

        prompt = f"""
You are an expert Python engineer.

Below is my complete project.

{codebase}

Explain:

1. Project Architecture
2. Important Files
3. Suggestions
4. Bugs
"""

        response = llm.invoke(prompt)

        print("\nAgent:\n")
        print(response.content)

        continue

    # -----------------------------
    # Planner
    # -----------------------------
    action = plan(user)

    print(f"🧠 Planner: {action}")
        # -----------------------------
    # READ
    # -----------------------------
    if action == "READ":

        filename = user.replace("read ", "").strip()

        print("\n📄 File Content:\n")
        print(read_file(filename))

        continue


    # -----------------------------
    # CREATE
    # -----------------------------
    if action == "CREATE":

        prompt = user.replace("create ", "").strip()

        parts = prompt.split(" ", 1)

        if len(parts) < 2:
            print("Usage:")
            print("create hello.py print hello world")
            continue

        filename = parts[0]
        task = parts[1]

        print("\n🤖 Generating code...\n")

        # Generate code
        code = generate_code(task)

        # Review code
        code = review_code(code)

        # Save file
        print(write_file(filename, code))

        # Run file
        print("\n▶ Running generated code...\n")

        output = run_python(filename)

        print(output)

        # Save to memory
        save_memory(user, output)

        # Auto Debug
        if "Traceback" in output:

            print("\n🐞 Error detected!")
            print("🤖 AI is fixing the code...\n")

            fixed_code = fix_code(code, output)

            write_file(filename, fixed_code)

            print("✅ Code fixed!")

            print("\n▶ Running fixed code...\n")

            output = run_python(filename)

            print(output)

        continue


    # -----------------------------
    # RUN
    # -----------------------------
    if action == "RUN":

        filename = user.replace("run ", "").strip()

        print("\n▶ Running...\n")

        output = run_python(filename)

        print(output)

        save_memory(user, output)

        if "Traceback" in output:

            print("\n🐞 Error detected!")
            print("🤖 AI is fixing the code...\n")

            code = read_file(filename)

            fixed_code = fix_code(code, output)

            write_file(filename, fixed_code)

            print("✅ Code fixed!")

            print("\n▶ Running fixed code...\n")

            output = run_python(filename)

            print(output)

        else:

            print("\n✅ Program executed successfully.")

        continue
        # -----------------------------
    # CHAT
    # -----------------------------
    history = get_memory()

    context = ""

    for chat in history:
        context += f"User: {chat['user']}\n"
        context += f"Assistant: {chat['assistant']}\n\n"

    messages = [
        SystemMessage(
            content=(
                "You are a helpful AI assistant.\n"
                "Use the previous conversation as memory.\n"
                "If the answer exists in the memory, use it.\n"
                "If it doesn't exist, answer normally."
            )
        ),
        HumanMessage(
            content=f"""
Previous Conversation:
{context}

Current User:
{user}
"""
        )
    ]

    response = llm.invoke(messages)

    save_memory(user, response.content)

    print("\nAgent:")
    print(response.content)
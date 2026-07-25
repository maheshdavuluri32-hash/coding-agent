from langchain_ollama import ChatOllama

from tools.file_reader import read_file
from tools.writer import write_file
from tools.executor import run_python

from agents.planner import plan
from agents.coder import generate_code
from agents.reviewer import review_code
from agents.debugger import fix_code


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
print("exit")
print("=" * 50)


# -----------------------------
# Main Loop
# -----------------------------
while True:

    user = input("\nYou: ").strip()

    # Exit
    if user.lower() == "exit":
        print("Goodbye!")
        break

    # Planner
    action = plan(user)
    print(f"🧠 Planner: {action}")

    # -----------------------------
    # Read File
    # -----------------------------
    if action == "READ":

        filename = user.replace("read ", "").strip()

        print("\n📄 File Content:\n")
        print(read_file(filename))

        continue

    # -----------------------------
    # Create File
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

        # Generate Code
        code = generate_code(task)

        # Review Code
        code = review_code(code)

        # Save File
        print(write_file(filename, code))

        # Run File
        print("\n▶ Running generated code...\n")

        output = run_python(filename)

        print(output)

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
    # Run Existing File
    # -----------------------------
    if action == "RUN":

        filename = user.replace("run ", "").strip()

        print("\n▶ Running...\n")

        output = run_python(filename)

        print(output)

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
    # Normal Chat
    # -----------------------------
    response = llm.invoke(user)

    print("\nAgent:")
    print(response.content)
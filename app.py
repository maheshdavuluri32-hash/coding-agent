"""
app.py

Single-file Streamlit frontend + backend for the AI coding agent.
Run with:  streamlit run app.py
"""

import streamlit as st

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from tools.file_reader import read_file
from tools.writer import write_file
from tools.compiler import run_program
from tools.project_reader import read_project
from tools.project_writer import get_python_files

from agents.planner import plan
from agents.coder import generate_code
from agents.reviewer import review_code
from agents.project_reviewer import review_project
from agents.debugger import fix_code
from agents.refactor import refactor_code
from tools.symbol_search import find_symbol
from agents.router import route

from rag.retriever import retrieve

from memory.chat_memory import (
    save_memory,
    get_memory,
    clear_memory,
)


# -----------------------------
# LLM
# -----------------------------
llm = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0,
)


# -----------------------------
# Helpers
# -----------------------------
def strip_prefix(text: str, prefix: str) -> str:
    """Remove only a leading prefix (not any occurrence of it)."""
    if text.lower().startswith(prefix):
        return text[len(prefix):].strip()
    return text.strip()


def format_code_block(filename: str, code: str, label: str = "Code") -> str:
    """
    Wrap code in a fenced markdown block so Streamlit's st.markdown
    renders it with syntax highlighting in the chat UI.
    """
    lang = "python" if filename.endswith(".py") else ""
    return f"\n📄 **{label} (`{filename}`):**\n```{lang}\n{code}\n```\n"


def process_user_input(user):
    """
    Route the user's input and build up file_context from any
    files or symbols the router detected.

    Returns:
        router (dict): the routing result (contains "files", "symbol", etc.)
        file_context (str): concatenated contents of any detected files
        notes (list[str]): human-readable notes for the frontend to show
    """
    router = route(user)

    files = router["files"]

    file_context = ""
    notes = []

    if files:
        notes.append(f"📂 Files: {files}")

        for file in files:
            code = read_file(file)

            file_context += f"""

========== {file} ==========

{code}

"""

    if router.get("symbol"):
        path = router["symbol"]

        notes.append(f"🔍 Symbol found in: {path}")

        code = read_file(path)

        file_context += f"""

========== {path} ==========

{code}

"""

    return router, file_context, notes


# -----------------------------
# Command handlers
# Each returns a plain string that the frontend can display.
# -----------------------------
def handle_memory():
    history = get_memory()

    if len(history) == 0:
        return "No conversation history."

    lines = ["📚 Conversation History:\n"]
    for chat in history:
        lines.append(f"**You:** {chat['user']}")
        lines.append(f"**AI:** {chat['assistant']}")
        lines.append("---")

    return "\n\n".join(lines)


def handle_clear():
    clear_memory()
    return "✅ Memory cleared."


def handle_project():
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

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"❌ LLM error: {e}"


def handle_search(query):
    docs = retrieve(query)

    if not docs:
        return "❌ No relevant files found."

    context = "\n\n".join(docs)

    prompt = f"""
You are an expert Python engineer.

Use ONLY the retrieved project files below to answer.

Retrieved Files:
{context}

Question:
{query}
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"❌ LLM error: {e}"


def handle_read(filename):
    code = read_file(filename)

    if code == "File not found.":
        return "❌ File not found."

    return format_code_block(filename, code, label="File contents")


def handle_create(user_text):
    prompt = strip_prefix(user_text, "create ")
    parts = prompt.split(" ", 1)

    if len(parts) < 2:
        return "Usage:\ncreate hello.py print hello world"

    filename = parts[0]
    task = parts[1]

    output_lines = ["🤖 Generating code..."]

    code = generate_code(filename, task)
    code = review_code(code)

    output_lines.append(write_file(filename, code))

    # Show the generated code in the UI
    output_lines.append(format_code_block(filename, code, label="Generated code"))

    output_lines.append("\n▶ Running program...\n")

    output = run_program(filename)
    output_lines.append(output)

    save_memory(user_text, output)

    if "Traceback" in output and filename.endswith(".py"):
        output_lines.append("\n🐞 Error detected!")
        output_lines.append("🤖 AI is fixing the code...")

        fixed_code = fix_code(code, output)
        write_file(filename, fixed_code)

        # Show the fixed code in the UI
        output_lines.append(format_code_block(filename, fixed_code, label="Fixed code"))

        output_lines.append("✅ Code fixed!")
        output_lines.append("\n▶ Running fixed code...\n")

        output = run_program(filename)
        output_lines.append(output)

    return "\n".join(output_lines)


def handle_run(user_text):
    filename = strip_prefix(user_text, "run ")

    output_lines = ["▶ Running...\n"]

    output = run_program(filename)
    output_lines.append(output)

    save_memory(user_text, output)

    if "Traceback" in output:
        output_lines.append("\n🐞 Error detected!")
        output_lines.append("🤖 AI is fixing the code...")

        code = read_file(filename)
        fixed_code = fix_code(code, output)
        write_file(filename, fixed_code)

        # Show the fixed code in the UI
        output_lines.append(format_code_block(filename, fixed_code, label="Fixed code"))

        output_lines.append("✅ Code fixed!")
        output_lines.append("\n▶ Running fixed code...\n")

        output = run_program(filename)
        output_lines.append(output)
    else:
        output_lines.append("\n✅ Program executed successfully.")

    return "\n".join(output_lines)


def handle_review(filename):
    code = read_file(filename)
    return review_code(code)


def handle_review_project():
    codebase = read_project()
    return review_project(codebase)


def handle_refactor_project():
    files = get_python_files()
    output_lines = []

    for file in files:
        output_lines.append(f"🤖 Refactoring {file}...")

        code = read_file(file)

        if code == "File not found.":
            continue

        try:
            new_code = refactor_code(code)
            write_file(file, new_code)

            # Show the refactored code in the UI
            output_lines.append(format_code_block(file, new_code, label="Refactored code"))
            output_lines.append(f"✅ {file} updated.")
        except Exception as e:
            output_lines.append(f"❌ Failed to refactor {file}")
            output_lines.append(str(e))

    output_lines.append("\n🎉 Project refactored successfully!")
    return "\n".join(output_lines)


def handle_debug(filename):
    code = read_file(filename)

    if code == "File not found.":
        return "❌ File not found."

    prompt = f"""
You are an expert software engineer.

Find all bugs in the following code.

Fix the code completely.

Return ONLY the corrected code.

Code:
{code}
"""

    try:
        response = llm.invoke(prompt)
    except Exception as e:
        return f"❌ LLM error: {e}"

    fixed_code = response.content.replace("```python", "").replace("```", "").strip()
    write_file(filename, fixed_code)

    output = run_program(filename)

    code_block = format_code_block(filename, fixed_code, label="Fixed code")

    return (
        f"✅ Code fixed successfully!\n"
        f"{code_block}\n"
        f"▶ Running fixed code...\n\n{output}"
    )


def handle_explain(filename):
    code = read_file(filename)

    if code == "File not found.":
        return "❌ File not found."

    prompt = f"""
You are an expert software engineer.

Explain the following code in detail.

Include:
1. Purpose
2. Working
3. Important functions
4. Logic
5. Improvements

Code:
{code}
"""

    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"❌ LLM error: {e}"


def handle_chat(user_text, file_context):
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
{user_text}

Referenced Files:
{file_context}

Instructions:
- If the user mentions a detected file, answer using ONLY that file's contents.
- Never guess what a file contains.
- If no files were detected, answer normally.
"""
        )
    ]

    try:
        response = llm.invoke(messages)
        save_memory(user_text, response.content)
        return response.content
    except Exception as e:
        return f"❌ LLM error: {e}"


# -----------------------------
# Single entry point for the frontend
# -----------------------------
def handle_message(user_text):
    """
    Main dispatcher. Takes raw user text, routes it through the same
    logic the CLI used to use, and returns a plain string response
    (plus a list of notes, e.g. detected files) for the frontend to render.
    """
    user_text = user_text.strip()

    router, file_context, notes = process_user_input(user_text)

    lower = user_text.lower()

    # Built-in commands
    if lower == "memory":
        return handle_memory(), notes

    if lower == "clear":
        return handle_clear(), notes

    if lower == "project":
        return handle_project(), notes

    if lower.startswith("search "):
        query = strip_prefix(user_text, "search ")
        return handle_search(query), notes

    # Planner-driven actions
    action = plan(user_text)
    notes.append(f"🧠 Planner: {action}")

    if action == "READ":
        filename = strip_prefix(user_text, "read ")
        return handle_read(filename), notes

    elif action == "CREATE":
        return handle_create(user_text), notes

    elif action == "RUN":
        return handle_run(user_text), notes

    elif action == "REVIEW":
        filename = strip_prefix(user_text, "review ")
        return handle_review(filename), notes

    elif action == "REVIEW_PROJECT":
        return handle_review_project(), notes

    elif action == "REFACTOR_PROJECT":
        return handle_refactor_project(), notes

    elif action == "DEBUG":
        filename = strip_prefix(user_text, "debug ")
        return handle_debug(filename), notes

    elif action == "EXPLAIN":
        filename = strip_prefix(user_text, "explain ")
        return handle_explain(filename), notes

    elif action == "SEARCH":
        query = strip_prefix(user_text, "search ")
        return handle_search(query), notes

    else:
        return handle_chat(user_text, file_context), notes


# =====================================================
# STREAMLIT FRONTEND
# =====================================================
st.set_page_config(page_title="AI Coding Agent", page_icon="🤖", layout="wide")

st.title("🤖 AI Coding Agent")

with st.sidebar:
    st.header("Commands")
    st.markdown(
        """
- `read <filename>`
- `create <filename> <task>`
- `run <filename>`
- `review <filename>`
- `debug <filename>`
- `explain <filename>`
- `search <query>`
- `project` — explain whole project
- `memory` — show conversation history
- `clear` — clear memory
        """
    )

    st.divider()

    if st.button("📚 Show memory"):
        st.session_state.setdefault("chat_history", [])
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": handle_memory(), "notes": []}
        )

    if st.button("🗑️ Clear memory"):
        st.session_state.setdefault("chat_history", [])
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": handle_clear(), "notes": []}
        )

    if st.button("🧹 Clear chat window"):
        st.session_state["chat_history"] = []


# -----------------------------
# Session state
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


# -----------------------------
# Render chat history
# -----------------------------
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        for note in msg.get("notes", []):
            st.caption(note)
        st.markdown(msg["content"])


# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input("Type a command or ask a question...")

if user_input:
    st.session_state["chat_history"].append(
        {"role": "user", "content": user_input, "notes": []}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response, notes = handle_message(user_input)
            except Exception as e:
                response, notes = f"❌ Error: {e}", []

        for note in notes:
            st.caption(note)
        st.markdown(response)

    st.session_state["chat_history"].append(
        {"role": "assistant", "content": response, "notes": notes}
    )
        
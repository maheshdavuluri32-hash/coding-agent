"""
app.py

Single-file Streamlit frontend + backend for the AI Coding Agent.

Run locally:
    streamlit run app.py

Streamlit Cloud:
    Add OLLAMA_API_KEY to App Settings -> Secrets
"""

import streamlit as st
from utils.llm_client import llm
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

from agents.router import route

from rag.retriever import retrieve

from memory.chat_memory import (
    save_memory,
    get_memory,
    clear_memory,
)


# ============================================================
# OLLAMA CLOUD
# ============================================================

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)

class LLMResponse:
    """
    Small wrapper so the rest of the application
    can continue using response.content
    """

    def __init__(self, content: str):
        self.content = content


class OllamaCloudLLM:
    """
    Wrapper around Ollama Cloud.

    Supports:

        llm.invoke("prompt")

    and:

        llm.invoke([
            SystemMessage(...),
            HumanMessage(...)
        ])
    """

    ROLE_MAP = {
        "system": "system",
        "human": "user",
        "ai": "assistant",
    }

    def __init__(
        self,
        model="gpt-oss:120b-cloud",
        temperature=0,
    ):
        self.model = model
        self.temperature = temperature

    def invoke(self, prompt_or_messages):

        # ----------------------------------------------------
        # SIMPLE STRING PROMPT
        # ----------------------------------------------------

        if isinstance(prompt_or_messages, str):

            messages = [
                {
                    "role": "user",
                    "content": prompt_or_messages,
                }
            ]

        # ----------------------------------------------------
        # LANGCHAIN MESSAGES
        # ----------------------------------------------------

        else:

            messages = []

            for message in prompt_or_messages:

                role = self.ROLE_MAP.get(
                    message.type,
                    "user",
                )

                messages.append(
                    {
                        "role": role,
                        "content": message.content,
                    }
                )

    




# ============================================================
# HELPERS
# ============================================================

def strip_prefix(text: str, prefix: str) -> str:
    """
    Remove only a leading prefix.
    """

    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):].strip()

    return text.strip()


def format_code_block(
    filename: str,
    code: str,
    label: str = "Code",
) -> str:
    """
    Format code for Streamlit.
    """

    extension = filename.split(".")[-1].lower()

    language_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "json": "json",
    }

    language = language_map.get(
        extension,
        "",
    )

    return (
        f"\n📄 **{label} (`{filename}`):**\n"
        f"```{language}\n"
        f"{code}\n"
        f"```\n"
    )


# ============================================================
# PROCESS USER INPUT
# ============================================================

def process_user_input(user):
    """
    Route the user's input and detect files/symbols.
    """

    router_result = route(user)

    files = router_result.get("files", [])

    file_context = ""

    notes = []

    # --------------------------------------------------------
    # DETECTED FILES
    # --------------------------------------------------------

    if files:

        notes.append(
            f"📂 Files: {files}"
        )

        for file in files:

            code = read_file(file)

            file_context += (
                f"\n========== {file} ==========\n"
                f"{code}\n"
            )

    # --------------------------------------------------------
    # DETECTED SYMBOL
    # --------------------------------------------------------

    if router_result.get("symbol"):

        path = router_result["symbol"]

        notes.append(
            f"🔍 Symbol found in: {path}"
        )

        code = read_file(path)

        file_context += (
            f"\n========== {path} ==========\n"
            f"{code}\n"
        )

    return (
        router_result,
        file_context,
        notes,
    )


# ============================================================
# MEMORY
# ============================================================

def handle_memory():

    history = get_memory()

    if not history:
        return "No conversation history."

    lines = [
        "📚 **Conversation History:**\n"
    ]

    for chat in history:

        lines.append(
            f"**You:** {chat['user']}"
        )

        lines.append(
            f"**AI:** {chat['assistant']}"
        )

        lines.append("---")

    return "\n\n".join(lines)


def handle_clear():

    clear_memory()

    return "✅ Memory cleared."


# ============================================================
# PROJECT
# ============================================================

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
5. Improvements

Be clear and practical.
"""

    try:

        response = llm.invoke(prompt)

        return response.content

    except Exception as e:

        return f"❌ LLM error: {e}"


# ============================================================
# SEARCH
# ============================================================

def handle_search(query):

    docs = retrieve(query)

    if not docs:

        return "❌ No relevant files found."

    context = "\n\n".join(docs)

    prompt = f"""
You are an expert Python engineer.

Use ONLY the retrieved project files below
to answer the user's question.

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


# ============================================================
# READ
# ============================================================

def handle_read(filename):

    code = read_file(filename)

    if code == "File not found.":

        return "❌ File not found."

    return format_code_block(
        filename,
        code,
        label="File contents",
    )


# ============================================================
# CREATE
# ============================================================

def handle_create(user_text):

    prompt = strip_prefix(
        user_text,
        "create ",
    )

    parts = prompt.split(" ", 1)

    if len(parts) < 2:

        return (
            "Usage:\n"
            "`create hello.py print hello world`"
        )

    filename = parts[0]

    task = parts[1]

    output_lines = [
        "🤖 Generating code..."
    ]

    try:

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        code = generate_code(
            filename,
            task,
        )

        # ----------------------------------------------------
        # REVIEW
        # ----------------------------------------------------

        if filename.endswith(".py"):

            code = review_code(code)

        # ----------------------------------------------------
        # WRITE
        # ----------------------------------------------------

        write_result = write_file(
            filename,
            code,
        )

        output_lines.append(
            write_result
        )

        output_lines.append(
            format_code_block(
                filename,
                code,
                label="Generated code",
            )
        )

        # ----------------------------------------------------
        # RUN
        # ----------------------------------------------------

        output_lines.append(
            "\n▶ Running program...\n"
        )

        output = run_program(filename)

        output_lines.append(
            output
        )

        save_memory(
            user_text,
            output,
        )

        # ----------------------------------------------------
        # AUTO DEBUG
        # ----------------------------------------------------

        if (
            "Traceback" in output
            and filename.endswith(".py")
        ):

            output_lines.append(
                "\n🐞 Error detected!"
            )

            output_lines.append(
                "🤖 AI is fixing the code..."
            )

            fixed_code = fix_code(
                code,
                output,
            )

            write_file(
                filename,
                fixed_code,
            )

            output_lines.append(
                format_code_block(
                    filename,
                    fixed_code,
                    label="Fixed code",
                )
            )

            output_lines.append(
                "✅ Code fixed!"
            )

            output_lines.append(
                "\n▶ Running fixed code...\n"
            )

            output = run_program(
                filename
            )

            output_lines.append(
                output
            )

        return "\n".join(
            output_lines
        )

    except Exception as e:

        return (
            "❌ Create operation failed:\n"
            f"{e}"
        )


# ============================================================
# RUN
# ============================================================

def handle_run(user_text):

    filename = strip_prefix(
        user_text,
        "run ",
    )

    output_lines = [
        "▶ Running...\n"
    ]

    try:

        output = run_program(
            filename
        )

        output_lines.append(
            output
        )

        save_memory(
            user_text,
            output,
        )

        # ----------------------------------------------------
        # AUTO DEBUG
        # ----------------------------------------------------

        if "Traceback" in output:

            output_lines.append(
                "\n🐞 Error detected!"
            )

            output_lines.append(
                "🤖 AI is fixing the code..."
            )

            code = read_file(
                filename
            )

            fixed_code = fix_code(
                code,
                output,
            )

            write_file(
                filename,
                fixed_code,
            )

            output_lines.append(
                format_code_block(
                    filename,
                    fixed_code,
                    label="Fixed code",
                )
            )

            output_lines.append(
                "✅ Code fixed!"
            )

            output_lines.append(
                "\n▶ Running fixed code...\n"
            )

            output = run_program(
                filename
            )

            output_lines.append(
                output
            )

        else:

            output_lines.append(
                "\n✅ Program executed successfully."
            )

        return "\n".join(
            output_lines
        )

    except Exception as e:

        return (
            "❌ Run failed:\n"
            f"{e}"
        )


# ============================================================
# REVIEW FILE
# ============================================================

def handle_review(filename):

    code = read_file(filename)

    if code == "File not found.":

        return "❌ File not found."

    try:

        return review_code(code)

    except Exception as e:

        return (
            "❌ Review failed:\n"
            f"{e}"
        )


# ============================================================
# REVIEW PROJECT
# ============================================================

def handle_review_project():

    codebase = read_project()

    try:

        return review_project(
            codebase
        )

    except Exception as e:

        return (
            "❌ Project review failed:\n"
            f"{e}"
        )


# ============================================================
# REFACTOR PROJECT
# ============================================================

def handle_refactor_project():

    files = get_python_files()

    if not files:

        return (
            "❌ No Python files found."
        )

    output_lines = []

    for file in files:

        output_lines.append(
            f"🤖 Refactoring `{file}`..."
        )

        code = read_file(file)

        if code == "File not found.":

            continue

        try:

            new_code = refactor_code(
                code
            )

            write_file(
                file,
                new_code,
            )

            output_lines.append(
                format_code_block(
                    file,
                    new_code,
                    label="Refactored code",
                )
            )

            output_lines.append(
                f"✅ `{file}` updated."
            )

        except Exception as e:

            output_lines.append(
                f"❌ Failed to refactor {file}"
            )

            output_lines.append(
                str(e)
            )

    output_lines.append(
        "\n🎉 Project refactoring completed!"
    )

    return "\n".join(
        output_lines
    )


# ============================================================
# DEBUG
# ============================================================

def handle_debug(filename):

    code = read_file(
        filename
    )

    if code == "File not found.":

        return "❌ File not found."

    prompt = f"""
You are an expert software engineer.

Find all bugs in the following code.

Fix the code completely.

Return ONLY the corrected code.

Rules:

- Return ONLY Python code.
- Do not use markdown.
- Do not use triple backticks.
- Do not explain anything.

Code:

{code}
"""

    try:

        response = llm.invoke(
            prompt
        )

        fixed_code = (
            response.content
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )

        write_file(
            filename,
            fixed_code,
        )

        output = run_program(
            filename
        )

        code_block = format_code_block(
            filename,
            fixed_code,
            label="Fixed code",
        )

        return (
            "✅ Code fixed successfully!\n"
            f"{code_block}\n"
            "▶ Running fixed code...\n\n"
            f"{output}"
        )

    except Exception as e:

        return (
            "❌ Debug failed:\n"
            f"{e}"
        )


# ============================================================
# EXPLAIN
# ============================================================

def handle_explain(filename):

    code = read_file(
        filename
    )

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

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as e:

        return (
            "❌ Explain failed:\n"
            f"{e}"
        )


# ============================================================
# CHAT
# ============================================================

def handle_chat(
    user_text,
    file_context,
):

    history = get_memory()

    context = ""

    for chat in history:

        context += (
            f"User: {chat['user']}\n"
        )

        context += (
            f"Assistant: "
            f"{chat['assistant']}\n\n"
        )

    messages = [

        SystemMessage(
            content=(
                "You are a helpful AI assistant.\n"
                "Use previous conversation as memory.\n"
                "If the answer exists in memory, "
                "use it.\n"
                "If it does not exist, answer normally."
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

- If the user mentions a detected file,
  answer using ONLY that file's contents.
- Never guess what a file contains.
- If no files were detected,
  answer normally.
"""
        ),
    ]

    try:

        response = llm.invoke(
            messages
        )

        save_memory(
            user_text,
            response.content,
        )

        return response.content

    except Exception as e:

        return (
            f"❌ LLM error: {e}"
        )


# ============================================================
# MAIN MESSAGE HANDLER
# ============================================================

def handle_message(user_text):

    """
    Main dispatcher.
    """

    user_text = user_text.strip()

    router_result, file_context, notes = (
        process_user_input(
            user_text
        )
    )

    lower = user_text.lower()

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if lower == "memory":

        return (
            handle_memory(),
            notes,
        )

    # --------------------------------------------------------
    # CLEAR MEMORY
    # --------------------------------------------------------

    if lower == "clear":

        return (
            handle_clear(),
            notes,
        )

    # --------------------------------------------------------
    # PROJECT
    # --------------------------------------------------------

    if lower == "project":

        return (
            handle_project(),
            notes,
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if lower.startswith("search "):

        query = strip_prefix(
            user_text,
            "search ",
        )

        return (
            handle_search(query),
            notes,
        )

    # --------------------------------------------------------
    # PLANNER
    # --------------------------------------------------------

    action = plan(
        user_text
    )

    notes.append(
        f"🧠 Planner: {action}"
    )

    # --------------------------------------------------------
    # READ
    # --------------------------------------------------------

    if action == "READ":

        filename = strip_prefix(
            user_text,
            "read ",
        )

        return (
            handle_read(filename),
            notes,
        )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    elif action == "CREATE":

        return (
            handle_create(user_text),
            notes,
        )

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    elif action == "RUN":

        return (
            handle_run(user_text),
            notes,
        )

    # --------------------------------------------------------
    # REVIEW
    # --------------------------------------------------------

    elif action == "REVIEW":

        filename = strip_prefix(
            user_text,
            "review ",
        )

        return (
            handle_review(filename),
            notes,
        )

    # --------------------------------------------------------
    # REVIEW PROJECT
    # --------------------------------------------------------

    elif action == "REVIEW_PROJECT":

        return (
            handle_review_project(),
            notes,
        )

    # --------------------------------------------------------
    # REFACTOR PROJECT
    # --------------------------------------------------------

    elif action == "REFACTOR_PROJECT":

        return (
            handle_refactor_project(),
            notes,
        )

    # --------------------------------------------------------
    # DEBUG
    # --------------------------------------------------------

    elif action == "DEBUG":

        filename = strip_prefix(
            user_text,
            "debug ",
        )

        return (
            handle_debug(filename),
            notes,
        )

    # --------------------------------------------------------
    # EXPLAIN
    # --------------------------------------------------------

    elif action == "EXPLAIN":

        filename = strip_prefix(
            user_text,
            "explain ",
        )

        return (
            handle_explain(filename),
            notes,
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    elif action == "SEARCH":

        query = strip_prefix(
            user_text,
            "search ",
        )

        return (
            handle_search(query),
            notes,
        )

    # --------------------------------------------------------
    # NORMAL CHAT
    # --------------------------------------------------------

    else:

        return (
            handle_chat(
                user_text,
                file_context,
            ),
            notes,
        )


# ============================================================
# STREAMLIT FRONTEND
# ============================================================
# Everything below this line is UI-only. No backend/agent/tool
# logic has been changed — this only wires buttons and layout
# to the existing handle_message() / handle_*() functions above.
# ============================================================

st.set_page_config(
    page_title="AI Coding Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------
# GLOBAL STYLES
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---------- App shell ---------- */
    .stApp {
        background: #0e1117;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: #12151c;
        border-right: 1px solid #23262f;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    /* ---------- Header card ---------- */
    .agent-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px;
        border-radius: 12px;
        background: linear-gradient(135deg, #1b1f2a 0%, #14161d 100%);
        border: 1px solid #262a35;
        margin-bottom: 18px;
    }

    .agent-header h1 {
        font-size: 1.15rem;
        margin: 0;
        color: #f5f6fa;
        font-weight: 600;
    }

    .agent-header p {
        margin: 2px 0 0 0;
        font-size: 0.78rem;
        color: #8b8f9c;
    }

    .status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 999px;
        background: #14261c;
        border: 1px solid #1f4d33;
        font-size: 0.75rem;
        color: #7de3a3;
        white-space: nowrap;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #34d17c;
        box-shadow: 0 0 6px #34d17c;
    }

    /* ---------- Sidebar section label ---------- */
    .sidebar-label {
        font-size: 0.72rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6b7280;
        margin: 14px 0 6px 2px;
        font-weight: 600;
    }

    /* ---------- Sidebar buttons ---------- */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        background: #181b23;
        border: 1px solid #262a35;
        color: #d7d9e0;
        border-radius: 8px;
        padding: 0.45rem 0.7rem;
        font-size: 0.85rem;
        transition: all 0.15s ease;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: #21252f;
        border-color: #3b82f6;
        color: #ffffff;
    }

    section[data-testid="stSidebar"] .stButton button:active {
        background: #26314a;
    }

    /* Danger-style button (clear memory / clear chat) */
    div[data-testid="stSidebar"] div[data-testid="column"] .stButton button {
        font-size: 0.8rem;
    }

    /* ---------- Chat bubbles ---------- */
    .stChatMessage {
        border-radius: 12px;
    }

    /* ---------- Caption / notes ---------- */
    .stCaption {
        color: #6b7280 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "queued_command" not in st.session_state:
    st.session_state["queued_command"] = None


def queue_command(command: str):
    """
    Sidebar buttons call this instead of touching the chat
    input directly (Streamlit doesn't allow programmatically
    setting st.chat_input's value). The queued command is
    picked up and processed on the next run, exactly like a
    message typed by the user.
    """

    st.session_state["queued_command"] = command


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    """
    <div class="agent-header">
        <div>
            <h1>🤖 AI Coding Agent</h1>
            <p>Your AI-powered coding assistant</p>
        </div>
        <div class="status-pill">
            <span class="status-dot"></span>
            Local · Llama 3.2
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "### 🧭 Workspace"
    )

    # ----------------------------------------------------
    # QUICK / AI-LEVEL COMMANDS (single click, no input needed)
    # ----------------------------------------------------

    st.markdown(
        '<div class="sidebar-label">AI Commands</div>',
        unsafe_allow_html=True,
    )

    if st.button("🧠 Project overview", use_container_width=True):
        queue_command("project")

    if st.button("🔍 Review project", use_container_width=True):
        queue_command("review project")

    if st.button("♻️ Refactor project", use_container_width=True):
        queue_command("refactor project")

    # ----------------------------------------------------
    # FILE COMMANDS (need a filename / task -> small form)
    # ----------------------------------------------------

    st.markdown(
        '<div class="sidebar-label">File Commands</div>',
        unsafe_allow_html=True,
    )

    file_action = st.selectbox(
        "Action",
        (
            "read",
            "create",
            "run",
            "review",
            "debug",
            "explain",
        ),
        label_visibility="collapsed",
    )

    filename_input = st.text_input(
        "Filename",
        placeholder="e.g. hello.py",
        label_visibility="collapsed",
    )

    task_input = ""

    if file_action == "create":

        task_input = st.text_input(
            "Task",
            placeholder="e.g. print hello world",
            label_visibility="collapsed",
        )

    if st.button(
        f"▶ Run `{file_action}`",
        use_container_width=True,
        disabled=not filename_input,
    ):

        if file_action == "create":

            queue_command(
                f"create {filename_input} {task_input}".strip()
            )

        else:

            queue_command(
                f"{file_action} {filename_input}"
            )

    # ----------------------------------------------------
    # SEARCH
    # ----------------------------------------------------

    st.markdown(
        '<div class="sidebar-label">AI Search</div>',
        unsafe_allow_html=True,
    )

    search_query = st.text_input(
        "Search",
        placeholder="Ask about the codebase...",
        label_visibility="collapsed",
    )

    if st.button(
        "🔎 Search project",
        use_container_width=True,
        disabled=not search_query,
    ):

        queue_command(f"search {search_query}")

    # ----------------------------------------------------
    # MEMORY
    # ----------------------------------------------------

    st.markdown(
        '<div class="sidebar-label">Memory</div>',
        unsafe_allow_html=True,
    )

    mem_col1, mem_col2 = st.columns(2)

    with mem_col1:

        if st.button("📚 Show", use_container_width=True):
            queue_command("memory")

    with mem_col2:

        if st.button("🗑️ Clear", use_container_width=True):
            queue_command("clear")

    st.divider()

    if st.button("🧹 Clear chat window", use_container_width=True):
        st.session_state["chat_history"] = []
        st.rerun()

    st.caption(
        "💡 Tip: you can still type any of these commands "
        "directly in the chat box below."
    )


# ============================================================
# RENDER CHAT HISTORY
# ============================================================

if not st.session_state["chat_history"]:

    st.info(
        "👋 Start by typing a command below, or use the "
        "sidebar to run a quick action — e.g. **Project overview**, "
        "**read app.py**, or **create hello.py print hello world**."
    )

for msg in st.session_state["chat_history"]:

    with st.chat_message(msg["role"]):

        for note in msg.get("notes", []):
            st.caption(note)

        st.markdown(msg["content"])


# ============================================================
# INPUT HANDLING
# (chat box + queued sidebar commands funnel into the same
# processing path, so backend behavior is identical either way)
# ============================================================

user_input = st.chat_input(
    "Type a command or ask a question..."
)

if not user_input and st.session_state["queued_command"]:
    user_input = st.session_state["queued_command"]
    st.session_state["queued_command"] = None

if user_input:

    # --------------------------------------------------------
    # SHOW USER MESSAGE
    # --------------------------------------------------------

    st.session_state["chat_history"].append(
        {
            "role": "user",
            "content": user_input,
            "notes": [],
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🤖 AI is thinking..."):

            try:

                response, notes = handle_message(user_input)

            except Exception as e:

                response = (
                    "❌ Application error:\n\n"
                    f"{e}"
                )

                notes = []

        for note in notes:
            st.caption(note)

        st.markdown(response)

    # --------------------------------------------------------
    # SAVE CHAT
    # --------------------------------------------------------

    st.session_state["chat_history"].append(
        {
            "role": "assistant",
            "content": response,
            "notes": notes,
        }
    )
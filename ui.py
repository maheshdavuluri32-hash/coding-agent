import streamlit as st

st.set_page_config(
    page_title="Agentic AI Coding Assistant",
    page_icon="🤖",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🤖 AI Coding Assistant")
    st.markdown("---")

    st.subheader("📂 Project Files")
    st.button("app.py")
    st.button("planner.py")
    st.button("compiler.py")
    st.button("reviewer.py")

    st.markdown("---")

    st.subheader("⚡ Quick Actions")

    st.button("Create")
    st.button("Run")
    st.button("Review")
    st.button("Debug")
    st.button("Search")
    st.button("Refactor")

# Main Page
st.title("🤖 Agentic AI Coding Assistant")

st.caption("Built using Python • Ollama • LangChain • Qwen2.5-Coder")

st.markdown("---")

user_input = st.chat_input("Ask your AI...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        st.write("Backend integration coming next...")
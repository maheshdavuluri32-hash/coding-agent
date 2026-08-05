import streamlit as st

st.set_page_config(
    page_title="Test",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Agentic AI Coding Assistant")

st.success("✅ Streamlit is Working!")

st.write("Hello Mahesh 👋")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.write(f"Welcome {name}!")
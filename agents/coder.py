import re
import ast
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2",
    temperature=0,
)


def clean_code_output(raw_text: str) -> str:
    """Remove ALL markdown code fence lines, even duplicated/nested ones."""
    lines = raw_text.strip().splitlines()
    cleaned_lines = [
        line for line in lines
        if not re.match(r"^\s*```", line)
    ]
    return "\n".join(cleaned_lines).strip()


def is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def generate_code(filename: str, task: str, max_retries: int = 3):

    extension = filename.split(".")[-1].lower()

    language_map = {
        "py": "Python",
        "java": "Java",
        "c": "C",
        "cpp": "C++",
        "js": "JavaScript",
        "ts": "TypeScript",
        "html": "HTML",
        "css": "CSS",
        "json": "JSON",
        "sql": "SQL",
        "xml": "XML"
    }

    language = language_map.get(extension, "Text")

    prompt = f"""
You are an expert {language} programmer.

Generate ONLY executable {language} code.

Rules:

- Return ONLY code.
- No markdown.
- No explanations.
- No triple backticks.

Task:

{task}
"""

    for attempt in range(max_retries):

        response = llm.invoke(prompt)

        code = clean_code_output(response.content)

        if code:
            return code

    raise ValueError("Failed to generate code.")
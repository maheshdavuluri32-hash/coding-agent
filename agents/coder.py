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


def generate_code(task: str, max_retries: int = 3) -> str:
    prompt = f"""
You are an expert Python programmer.

Generate ONLY executable Python code.

Rules:
- Return ONLY valid Python code.
- DO NOT use markdown.
- DO NOT use triple backticks.
- DO NOT explain anything.
- The first line must be Python code.

Task:
{task}
"""

    for attempt in range(1, max_retries + 1):
        response = llm.invoke(prompt)
        raw = response.content

        print(f"\n===== RAW LLM OUTPUT (attempt {attempt}) =====")
        print(raw)
        print("==========================")

        code = clean_code_output(raw)

        if code and is_valid_python(code):
            return code

        print(f"Attempt {attempt}: generated code was not valid Python. Retrying...")

    raise ValueError(f"Failed to generate valid Python code after {max_retries} attempts.")


if __name__ == "__main__":
    task = "write a function that adds two numbers, then in a loop asks the user for two numbers with input validation, and prints the sum"
    code = generate_code(task)

    with open("add.py", "w") as f:
        f.write(code)

    print("\nSaved valid Python code to add.py")
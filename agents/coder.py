from utils.code_utils import (
    clean_code_output,
    is_valid_python
)

from utils.llm_client import llm


def generate_code(
    filename: str,
    task: str,
    max_retries: int = 3
):
    """Generate code using  Local Ollama ."""

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

Generate complete executable {language} code.

Task:
{task}

Rules:
- Return ONLY code.
- Do NOT use markdown.
- Do NOT use triple backticks.
- Do NOT explain anything.
"""

    last_error = None

    for attempt in range(1, max_retries + 1):

        try:
            print(f"🤖 Coder attempt {attempt}")

            response = llm.invoke(prompt)

            print("✅ Ollama response received")

            code = response.content

            print("Raw response:")
            print(code)

            code = clean_code_output(code)

            if not code:
                print("⚠️ Empty response.")
                continue

            if extension == "py":

                if is_valid_python(code):
                    print("✅ Valid Python generated")
                    return code

                print("⚠️ Generated Python is invalid.")
                continue

            return code

        except Exception as e:

            last_error = e

            print(
                f"❌ Coder attempt {attempt} failed:"
            )
            print(repr(e))

    raise ValueError(
        f"Failed to generate valid code. "
        f"Last error: {last_error}"
    )
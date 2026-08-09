from utils.code_utils import clean_code_output, is_valid_python
from ollama import Client
import os


ollama_client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]
    }
)


class LLMResponse:
    def __init__(self, content):
        self.content = content


def fix_code(code, error, max_retries=3):

    prompt = f"""
You are an expert Python programmer.

The following code has an error.

Code:
{code}

Error:
{error}

Rules:

- Return ONLY the corrected Python code.
- DO NOT use markdown.
- DO NOT use triple backticks.
- DO NOT explain anything.
"""

    for attempt in range(1, max_retries + 1):

        try:
            response = ollama_client.chat(
                model="gpt-oss:120b-cloud",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            fixed = response["message"]["content"]

            fixed = clean_code_output(fixed)

            if fixed and is_valid_python(fixed):
                return fixed

            print(
                f"Debugger attempt {attempt}: "
                "invalid Python returned. Retrying..."
            )

        except Exception as e:
            print(f"Debugger attempt {attempt} failed: {e}")

    print("⚠️ Debugger failed to return valid code. Keeping original.")

    return code
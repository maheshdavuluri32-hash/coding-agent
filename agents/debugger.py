from utils.llm_client import llm
from utils.code_utils import clean_code_output, is_valid_python


def fix_code(code, error, max_retries=3):
    """
    Automatically fix Python code based on the error output.
    """

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
            response = llm.invoke(prompt)

            fixed = clean_code_output(response.content)

            if fixed and is_valid_python(fixed):
                return fixed

            print(
                f"Debugger attempt {attempt}: "
                "invalid Python returned. Retrying..."
            )

        except Exception as e:
            print(
                f"Debugger attempt {attempt} failed: {e}"
            )

    print(
        "⚠️ Debugger failed to return valid code. "
        "Keeping original."
    )

    return code
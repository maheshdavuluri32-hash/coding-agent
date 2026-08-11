from utils.llm_client import llm
from utils.code_utils import clean_code_output, is_valid_python


def review_code(code, max_retries=3):
    """Review and improve Python code without changing its functionality."""

    prompt = f"""
You are a senior Python reviewer.

Review this code.

Rules:

- If the code is good, return it unchanged.
- If there are small improvements, apply them.
- Do not change the functionality.
- Return ONLY Python code.
- DO NOT use markdown.
- DO NOT use triple backticks.

Code:

{code}
"""

    for attempt in range(1, max_retries + 1):

        try:
            response = llm.invoke(prompt)

            reviewed = response.content

            reviewed = clean_code_output(reviewed)

            if reviewed and is_valid_python(reviewed):
                return reviewed

            print(
                f"Reviewer attempt {attempt}: "
                "invalid Python returned. Retrying..."
            )

        except Exception as e:
            print(
                f"Reviewer attempt {attempt} failed: {e}"
            )

    print(
        "⚠️ Reviewer failed to return valid code. "
        "Keeping original."
    )

    return code
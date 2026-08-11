from utils.llm_client import llm
from utils.code_utils import clean_code_output, is_valid_python


def refactor_code(code):
    """Refactor Python code while preserving its functionality."""

    prompt = f"""
You are a Senior Software Engineer.

Refactor the following code.

Requirements:

- Improve readability.
- Improve naming.
- Remove duplicate code.
- Improve performance.
- Follow best practices.
- Keep the same functionality.
- Return ONLY the refactored Python code.
- DO NOT use markdown.
- DO NOT use triple backticks.

Code:

{code}
"""

    try:
        response = llm.invoke(prompt)

        refactored_code = response.content

        refactored_code = clean_code_output(refactored_code)

        if refactored_code and is_valid_python(refactored_code):
            return refactored_code

        print("⚠️ Refactored code is not valid Python.")
        return code

    except Exception as e:
        print(f"❌ Refactor failed: {e}")
        return code
from utils.llm_client import llm


def convert_code(code, target_language):

    prompt = f"""
You are an expert software engineer.

Convert the following code into {target_language}.

Rules:
- Return ONLY code.
- No markdown.
- No explanation.
- No triple backticks.

Code:

{code}
"""

    response = llm.invoke(prompt)

    return (
        response.content
        .replace("```python", "")
        .replace("```", "")
        .strip()
    )
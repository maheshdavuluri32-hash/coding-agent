import re
import ast


def clean_code_output(raw_text: str) -> str:
    """Remove markdown code fences from LLM output."""

    if not raw_text:
        return ""

    lines = raw_text.strip().splitlines()

    cleaned_lines = [
        line
        for line in lines
        if not re.match(r"^\s*```", line)
    ]

    return "\n".join(cleaned_lines).strip()


def is_valid_python(code: str) -> bool:
    """Check whether the generated code is valid Python."""

    if not code:
        return False

    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
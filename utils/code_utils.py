import re
import ast


def clean_code_output(raw_text: str) -> str:
    """Remove markdown fences, then trim trailing non-code lines (explanations, notes, etc.)."""
    lines = raw_text.strip().splitlines()

    # Strip any fence lines first
    lines = [line for line in lines if not re.match(r"^\s*```", line)]

    text = "\n".join(lines).strip()

    # If it already parses cleanly, we're done
    if is_valid_python(text):
        return text

    # Otherwise, trim trailing lines one at a time until it parses
    lines = text.splitlines()
    while lines:
        candidate = "\n".join(lines).strip()
        if is_valid_python(candidate):
            return candidate
        lines.pop()

    # Nothing parsed — return best-effort original (caller will retry/reject)
    return text


def is_valid_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
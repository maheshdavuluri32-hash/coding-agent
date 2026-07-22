from pathlib import Path

def read_file(path: str):
    try:
        file = Path(path)

        if not file.exists():
            return "File not found."

        return file.read_text(encoding="utf-8")

    except Exception as e:
        return str(e)
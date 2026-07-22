from pathlib import Path

def write_file(file_path: str, content: str):
    try:
        path = Path(file_path)
        path.write_text(content, encoding="utf-8")
        return f"✅ File '{file_path}' created successfully."

    except Exception as e:
        return f"Error: {e}"
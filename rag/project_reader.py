import os

def read_project(project_path="."):

    project_text = ""

    for root, dirs, files in os.walk(project_path):

        # Skip unnecessary folders
        dirs[:] = [
            d for d in dirs
            if d not in [".venv", "__pycache__", ".git"]
        ]

        for file in files:

            if file.endswith(".py"):

                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:

                        project_text += f"\n\n===== {path} =====\n"
                        project_text += f.read()

                except Exception:
                    pass

    return project_text
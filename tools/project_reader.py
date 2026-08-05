import os


def read_project():

    project = ""

    for root, dirs, files in os.walk("."):

        # Skip unwanted folders
        dirs[:] = [
            d for d in dirs
            if d not in [
                ".venv",
                "__pycache__",
                ".git",
                "chroma_db"
            ]
        ]

        for file in files:

            if file.endswith(".py"):

                path = os.path.join(root, file)

                with open(path, "r", encoding="utf-8") as f:

                    project += f"\n\n===== {path} =====\n"

                    project += f.read()

    return project
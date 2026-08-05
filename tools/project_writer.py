import os


def get_python_files():

    files = []

    for root, dirs, filenames in os.walk("."):

        dirs[:] = [
            d for d in dirs
            if d not in [
                ".venv",
                "__pycache__",
                ".git",
                "chroma_db"
            ]
        ]

        for file in filenames:

            if file.endswith(".py"):

                files.append(os.path.join(root, file))

    return files
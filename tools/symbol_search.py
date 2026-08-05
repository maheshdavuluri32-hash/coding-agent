import os
import re


def find_symbol(symbol):

    for root, dirs, files in os.walk("."):

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

            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            try:

                with open(path, "r", encoding="utf-8") as f:

                    code = f.read()

                # function
                if re.search(rf"def\s+{re.escape(symbol)}\s*\(", code):

                    return path

                # class
                if re.search(rf"class\s+{re.escape(symbol)}\b", code):

                    return path

            except:
                pass

    return None
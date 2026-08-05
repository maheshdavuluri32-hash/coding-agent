import os
import re


def detect_files(user_input):

    found = []

    # Find anything ending with a file extension
    matches = re.findall(r"[\w./\\-]+\.[a-zA-Z0-9]+", user_input)

    for file in matches:

        if os.path.exists(file):
            found.append(file)

    return found
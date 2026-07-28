import json
import os

MEMORY_FILE = "memory/memory.json"


def load_memory():

    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        return []


def save_memory(user, assistant):

    history = load_memory()

    history.append({
        "user": user,
        "assistant": assistant
    })

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)


def get_memory():
    return load_memory()


def clear_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump([], file, indent=4)
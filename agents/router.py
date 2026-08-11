from tools.file_detector import detect_files
from tools.symbol_search import find_symbol


def route(user):
    result = {
        "files": [],
        "symbol": None,
        "project": False
    }

    # Detect files
    files = detect_files(user)

    if files:
        result["files"] = files
        return result

    # Detect project
    if "project" in user.lower():
        result["project"] = True
        return result

    # Detect function/class names
    words = user.replace("?", "").replace(",", "").split()

    for word in words:
        path = find_symbol(word)

        if path:
            result["symbol"] = path
            return result

    return result
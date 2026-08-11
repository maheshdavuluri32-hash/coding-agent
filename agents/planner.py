print("✅ Planner loaded")


def plan(user_input):
    print("User Input:", repr(user_input))

    user = user_input.lower().strip()

    if user.startswith("read "):
        print("Planner Decision: READ")
        return "READ"

    elif user.startswith("create "):
        print("Planner Decision: CREATE")
        return "CREATE"

    elif user.startswith("run "):
        print("Planner Decision: RUN")
        return "RUN"

    elif user == "refactor project":
        print("Planner Decision: REFACTOR_PROJECT")
        return "REFACTOR_PROJECT"

    elif user == "review project":
        print("Planner Decision: REVIEW_PROJECT")
        return "REVIEW_PROJECT"

    elif user.startswith("review "):
        print("Planner Decision: REVIEW")
        return "REVIEW"

    elif user.startswith("debug "):
        print("Planner Decision: DEBUG")
        return "DEBUG"

    elif user.startswith("explain "):
        print("Planner Decision: EXPLAIN")
        return "EXPLAIN"

    elif user.startswith("search "):
        print("Planner Decision: SEARCH")
        return "SEARCH"

    else:
        print("Planner Decision: CHAT")
        return "CHAT"
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

    else:
        print("Planner Decision: CHAT")
        return "CHAT"
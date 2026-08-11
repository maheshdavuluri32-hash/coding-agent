from utils.llm_client import llm


def review_project(codebase):
    """Review the complete software project."""

    prompt = f"""
You are a Senior Software Engineer.

Review this complete software project.

Give:

1. Architecture Review
2. Code Quality
3. Performance
4. Security
5. Best Practices
6. Folder Structure
7. Bugs
8. Improvements

Finally give an overall rating out of 10.

Project:

{codebase}
"""

    try:
        response = llm.invoke(prompt)

        return response.content

    except Exception as e:
        print(f"❌ Project review failed: {e}")
        return f"Project review failed: {e}"
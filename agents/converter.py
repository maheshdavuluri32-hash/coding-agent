from utils.llm_client import llm


def convert_code(code, target_language):
    """Convert code from its current language to another language."""

    prompt = f"""
You are an expert software engineer.

Convert the following code into {target_language}.

Rules:

- Return ONLY code.
- No markdown.
- No explanation.
- No triple backticks.
- Preserve the original functionality.
- Use best practices for {target_language}.

Code:

{code}
"""

    try:
        response = llm.invoke(prompt)

        converted_code = response.content

        # Remove markdown code fences if the model adds them.
        converted_code = (
            converted_code
            .replace("```python", "")
            .replace("```javascript", "")
            .replace("```java", "")
            .replace("```cpp", "")
            .replace("```c", "")
            .replace("```typescript", "")
            .replace("```html", "")
            .replace("```css", "")
            .replace("```sql", "")
            .replace("```", "")
            .strip()
        )

        return converted_code

    except Exception as e:
        print(f"❌ Code conversion failed: {e}")
        return code
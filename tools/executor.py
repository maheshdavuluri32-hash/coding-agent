import subprocess


def run_python(file_name):
    try:
        result = subprocess.run(
            ["python", file_name],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout

        return result.stderr

    except Exception as e:
        return str(e)
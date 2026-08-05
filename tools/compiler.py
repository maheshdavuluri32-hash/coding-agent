"""
tools/compiler.py

Runs a source file and returns its combined stdout+stderr output as a string.
Supports: .py, .java, .c, .cpp

Design:
- Each language gets a small handler function: (filepath) -> output string.
- run_program(filename) dispatches based on file extension.
- Compiled languages (java/c/cpp) compile into a temp build directory next
  to the source file, run the result, then clean up build artifacts.
- All subprocess calls are time-limited so a hanging program can't freeze
  the whole agent loop.
"""

import os
import subprocess
import shutil
import uuid

TIMEOUT_SECONDS = 15


def _run_subprocess(cmd, cwd=None, timeout=TIMEOUT_SECONDS):
    """
    Run a command, capture stdout+stderr together, and return it as text.
    Never raises for a failing program -- failures are returned as text
    output (e.g. containing 'Traceback' or a compiler error) so callers
    can inspect them.
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
        )
        output = result.stdout or ""

        if result.returncode != 0 and not output.strip():
            output = f"Process exited with code {result.returncode} and no output."

        return output

    except subprocess.TimeoutExpired:
        return f"⏱️ Timed out after {timeout}s. The program may be waiting on input or stuck in a loop."

    except FileNotFoundError as e:
        return f"❌ Required tool not found: {e}"

    except Exception as e:
        return f"❌ Unexpected error while running program: {e}"


# -----------------------------
# Python
# -----------------------------
def _run_python(filepath):
    return _run_subprocess(["python3", filepath])


# -----------------------------
# Java
# -----------------------------
def _run_java(filepath):
    """
    Java requires the public class name to match the filename, and javac/java
    both operate relative to a working directory. We compile in place (next
    to the .java file) then run the resulting .class, cleaning up after.
    """
    directory = os.path.dirname(os.path.abspath(filepath)) or "."
    filename = os.path.basename(filepath)
    class_name = os.path.splitext(filename)[0]
    class_file = os.path.join(directory, f"{class_name}.class")

    compile_output = _run_subprocess(["javac", filename], cwd=directory)

    # javac produces no stdout on success; only treat as failure if the
    # .class file wasn't actually produced.
    if not os.path.exists(class_file):
        if compile_output.strip():
            return f"❌ Compilation failed:\n{compile_output}"
        return "❌ Compilation failed: no .class file produced (check that the public class name matches the filename)."

    try:
        run_output = _run_subprocess(["java", class_name], cwd=directory)
        return run_output
    finally:
        # Clean up compiled .class files (including inner-class artifacts)
        for f in os.listdir(directory):
            if f.startswith(class_name) and f.endswith(".class"):
                try:
                    os.remove(os.path.join(directory, f))
                except OSError:
                    pass


# -----------------------------
# C
# -----------------------------
def _run_c(filepath):
    return _compile_and_run_native(filepath, compiler="gcc")


# -----------------------------
# C++
# -----------------------------
def _run_cpp(filepath):
    return _compile_and_run_native(filepath, compiler="g++")


def _compile_and_run_native(filepath, compiler):
    directory = os.path.dirname(os.path.abspath(filepath)) or "."
    filename = os.path.basename(filepath)
    binary_name = f".tmp_{uuid.uuid4().hex[:8]}"
    binary_path = os.path.join(directory, binary_name)

    compile_output = _run_subprocess(
        [compiler, filename, "-o", binary_name], cwd=directory
    )

    if not os.path.exists(binary_path):
        if compile_output.strip():
            return f"❌ Compilation failed:\n{compile_output}"
        return "❌ Compilation failed: no executable produced."

    try:
        run_output = _run_subprocess([f"./{binary_name}"], cwd=directory)
        return run_output
    finally:
        if os.path.exists(binary_path):
            try:
                os.remove(binary_path)
            except OSError:
                pass


# -----------------------------
# Dispatch table
# -----------------------------
_HANDLERS = {
    "py": _run_python,
    "java": _run_java,
    "c": _run_c,
    "cpp": _run_cpp,
    "cc": _run_cpp,
    "cxx": _run_cpp,
}


def run_program(filename):
    """
    Run a source file based on its extension and return combined output.
    Returns a plain error string (not an exception) for unsupported types,
    missing files, compile errors, or runtime errors -- callers can just
    print() the result or check it for 'Traceback' / '❌'.
    """
    if not os.path.exists(filename):
        return f"❌ File not found: {filename}"

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    handler = _HANDLERS.get(extension)

    if handler is None:
        return f"⚠️ Running .{extension} files is not supported yet."

    return handler(filename)
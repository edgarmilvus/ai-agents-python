import subprocess
import tempfile
import os
import sys
from typing import Tuple

# Define a type alias for clarity: (exit_code, stdout_content, stderr_content)
ExecutionResult = Tuple[int, str, str]

def execute_code(code_content: str, timeout: int = 5) -> ExecutionResult:
    """
    Executes Python code safely in a sandboxed subprocess and captures feedback.
    
    This function isolates the execution environment by running the code in a 
    separate process, ensuring that any errors or malicious operations do not 
    affect the main agent process.
    """
    temp_file_path = ""
    try:
        # 1. TEMPORARY FILE CREATION
        # Use tempfile to create a unique, non-colliding filename
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".py", encoding='utf-8') as tmp_file:
            tmp_file.write(code_content)
            temp_file_path = tmp_file.name

        # 2. COMMAND CONSTRUCTION
        # Use sys.executable to guarantee the code runs with the same Python interpreter 
        # that launched the agent, ensuring library compatibility.
        command = [sys.executable, temp_file_path]

        # 3. SUBPROCESS EXECUTION
        # subprocess.run handles the execution, capturing I/O streams.
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False # CRITICAL: Prevents Python from raising an exception on non-zero exit codes.
        )

        # 4. RESULT EXTRACTION
        # returncode 0 means success; non-zero means failure (syntax, runtime, etc.)
        return (
            process.returncode,
            process.stdout.strip(),
            process.stderr.strip()
        )

    except subprocess.TimeoutExpired:
        # Handle cases where the code runs longer than the defined timeout
        return (1, "", f"Execution timed out after {timeout} seconds. Potential infinite loop detected.")

    except Exception as e:
        # Catch unexpected internal errors (e.g., file permissions, OS issues)
        return (1, "", f"Internal sandbox error during execution setup: {e}")

    finally:
        # 5. CLEANUP
        # Ensure the temporary file is deleted, regardless of success or failure
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# --- DEMONSTRATION USAGE ---

# Case 1: Successful Execution (Exit Code 0, STDOUT captured)
SUCCESS_CODE = """
# Agent Goal: Write a function that calculates the square of a number.
def square(n):
    return n * n
print(f"The square of 11 is: {square(11)}")
"""
print("--- Running SUCCESS_CODE (Expected Success) ---")
exit_code, stdout, stderr = execute_code(SUCCESS_CODE)
print(f"Exit Code: {exit_code}")
print(f"STDOUT:\n{stdout}")
print(f"STDERR:\n{stderr}\n")

# Case 2: Runtime Error (Exit Code Non-Zero, STDERR captured)
RUNTIME_ERROR_CODE = """
# Agent Goal: Calculate a division result.
divisor = 0
result = 100 / divisor # ZeroDivisionError occurs here
print(f"Result: {result}")
"""
print("--- Running RUNTIME_ERROR_CODE (Expected Runtime Failure) ---")
exit_code, stdout, stderr = execute_code(RUNTIME_ERROR_CODE)
print(f"Exit Code: {exit_code}")
print(f"STDOUT:\n{stdout}")
print(f"STDERR:\n{stderr}\n")

# Case 3: Syntax Error (Exit Code Non-Zero, STDERR captured early by interpreter)
SYNTAX_ERROR_CODE = """
def test_syntax():
    # Missing colon and bad indentation
    if True
        print("Error") 
"""
print("--- Running SYNTAX_ERROR_CODE (Expected Syntax Failure) ---")
exit_code, stdout, stderr = execute_code(SYNTAX_ERROR_CODE)
print(f"Exit Code: {exit_code}")
print(f"STDOUT:\n{stdout}")
print(f"STDERR:\n{stderr}\n")

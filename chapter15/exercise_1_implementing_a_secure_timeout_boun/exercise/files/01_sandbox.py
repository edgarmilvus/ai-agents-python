import subprocess
import os
import sys
import tempfile
from typing import Dict, Any

# Define the timeout limit in seconds
TIMEOUT_LIMIT = 5

def execute_sandboxed_code(code_string: str) -> Dict[str, Any]:
    """
    Executes a string of Python code in an isolated subprocess with a timeout.

    Args:
        code_string: The Python code to execute.

    Returns:
        A dictionary containing execution results (success, output, errors, reason).
    """
    tmp_file_path = None
    
    # 1. Use a temporary file to store the code for clean execution.
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as tmp_file:
            tmp_file.write(code_string)
            tmp_file_path = tmp_file.name

        # 2. Define the command (shell=False for security)
        command = [sys.executable, tmp_file_path]

        # 3. Execute the process, capturing output and enforcing the timeout
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_LIMIT,
            check=False  # Do not raise CalledProcessError automatically
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        exit_code = result.returncode

        if exit_code == 0:
            # Successful execution
            return {
                'success': True,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': exit_code,
                'reason': 'Success'
            }
        else:
            # Non-zero exit code (runtime error or explicit sys.exit(N))
            reason = "Runtime Error or Non-Zero Exit Code"
            if stderr:
                # Capture the final error line for concise reason
                last_error_line = stderr.splitlines()[-1] if stderr.splitlines() else "Unknown Error"
                reason = f"Runtime Error: {last_error_line}"

            return {
                'success': False,
                'stdout': stdout,
                'stderr': stderr,
                'exit_code': exit_code,
                'reason': reason
            }

    except subprocess.TimeoutExpired:
        # Process was terminated due to timeout
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Execution timed out after {TIMEOUT_LIMIT} seconds.',
            'exit_code': -1,
            'reason': 'Timeout Error'
        }
    except Exception as e:
        # Catch unexpected errors during the subprocess management itself
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Executor internal error: {type(e).__name__}: {e}',
            'exit_code': -2,
            'reason': 'Internal Executor Failure'
        }
    finally:
        # 4. Clean up the temporary file
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# # Example Test Cases:
# print("--- Test 1: Success ---")
# code_success = "import sys; print('Success'); sys.exit(0)"
# print(execute_sandboxed_code(code_success))

# print("\n--- Test 2: Runtime Error ---")
# code_error = "x = 1 / 0"
# print(execute_sandboxed_code(code_error))

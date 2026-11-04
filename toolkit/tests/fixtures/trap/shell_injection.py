import subprocess


def run(code):
    return subprocess.run(f"python -c {code}", shell=True, capture_output=True)

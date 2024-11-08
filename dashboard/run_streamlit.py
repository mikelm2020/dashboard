import os
import subprocess

# Current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Running Streamlit in the virtual environment
subprocess.Popen(
    [
        r"C:\dashboard\.venv\Scripts\streamlit.exe",
        "run",
        os.path.join(script_dir, "app.py"),
    ],
    stdout=subprocess.DEVNULL,  # Redirect stdout to null
    stderr=subprocess.DEVNULL,  # Redirect standard errors to null
)

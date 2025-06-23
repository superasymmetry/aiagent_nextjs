import subprocess

python_script = r"C:\Users\2025130\Documents\aiagent_nextjs\vm\initialize.py"

subprocess.run([
    "powershell",
    "-Command",
    f"Start-Process python -ArgumentList '{python_script}' -Verb RunAs"
])
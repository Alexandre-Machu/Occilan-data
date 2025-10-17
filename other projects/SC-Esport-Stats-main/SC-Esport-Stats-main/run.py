import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    src_path = str(Path(__file__).parent / "src")
    subprocess.run(["streamlit", "run", f"{src_path}/app.py"])

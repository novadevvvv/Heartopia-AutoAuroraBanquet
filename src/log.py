import inspect
from pathlib import Path

def log(text: str):
    caller_file = inspect.stack()[1].filename
    file_name = Path(caller_file).stem
    print(f"[ {file_name} ] : {text}")

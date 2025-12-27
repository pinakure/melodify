from pathlib import Path

def saferead(filename, read_mode='r'):
    BASE_DIR = Path(__file__).resolve().parent
    filename = BASE_DIR / filename
    print(("-"*80)+"\n" + f"SAFEREAD: Trying to open '{filename}'", end="\n")
    with open(filename, read_mode) as f:
        return f.read()
    
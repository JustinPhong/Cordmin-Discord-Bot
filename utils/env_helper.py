from getpass import getpass
from pathlib import Path

def insert_env(key: str, label: str | None = None, value: str | None = None) -> str:
    if label is not None:
        value = input(f"Enter Discord {label}: ").strip()

    remove_env_key(key)

    with open(".env", "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")

    return value

def remove_env_key(key: str):
    if not Path(".env").exists():
        print("Env not exists")
        return

    lines = Path(".env").read_text(encoding="utf-8").splitlines()
    filtered = [
        line for line in lines
        if not line.startswith(f"{key}=")
    ]

    Path(".env").write_text("\n".join(filtered) + "\n", encoding="utf-8")
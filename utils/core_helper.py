import asyncio
import config
import sys
import os
import re
import json
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)
ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

def servertime() -> str:
    return f"[{datetime.now().strftime('%H:%M:%S')}]"

def log(text: str):
    time = servertime()
    message = f"{time} {text}"

    print(message)

    if getattr(config, "LOG_FILE", None):
        clean = strip_ansi(message)
        save_file(clean,filename=datetime.now().strftime("%d-%m-%Y.log"),folder="Logs")


def success(text: str):
    log(f"{Fore.GREEN}{text}")

def warning(text: str, e: Exception | None = None):
    if e:
        log(f"{Fore.YELLOW}{text}: {e}")
    else:
        log(f"{Fore.YELLOW}{text}")

def error(text: str, e: Exception | None = None):
    if e:
        log(f"{Fore.RED}{text}: {e}")
    else:
        log(f"{Fore.RED}{text}")

async def restart(error_msg: str) -> bool:
    answer = await async_input(f"{servertime()} {Fore.YELLOW}{error_msg}{Fore.RESET}, press Y to restart: ",timeout=5)
    if answer and answer.strip().lower() == "y":
        log("Restarting...")
        return True
    return False

async def async_input(prompt: str, timeout: int = 10):
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(loop.run_in_executor(None, input, prompt),timeout)
    except asyncio.TimeoutError:
        return None

def save_file(data: str, filename: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "a", encoding="utf-8") as f: f.write(data + "\n")

def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)
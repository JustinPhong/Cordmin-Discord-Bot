import asyncio
import sys
from datetime import datetime
from colorama import init, Fore

init()

async def restart(error: str) -> bool:
    answer = await async_input(f"[{datetime.now().strftime("%H:%M:%S")}] {Fore.YELLOW}{error}{Fore.RESET}, press Y to restart:\n", timeout=5)
    if answer and answer.strip().lower() == "y":
        log("Restarting...")
        return True
    else:
        return False

async def async_input(prompt: str, timeout: int = 10):
    loop = asyncio.get_running_loop()
    try:
        return await asyncio.wait_for(loop.run_in_executor(None, lambda: input(prompt)), timeout)
    except asyncio.TimeoutError:
        return None

def error(text: str, e: Exception | None = None):
    if e:
        log(f"{Fore.RED}{text}: {e}{Fore.RESET}")
    else:
        log(f"{Fore.RED}{text}{Fore.RESET}")

def warning(text: str, e: Exception | None = None):
    if e:
        log(f"{Fore.YELLOW}{text}: {e}{Fore.RESET}")
    else:
        log(f"{Fore.YELLOW}{text}{Fore.RESET}")

def success(text: str):
    log(f"{Fore.GREEN}{text}{Fore.RESET}")

def log(text:str):
    print(f"[{datetime.now().strftime("%H:%M:%S")}] {text}")

def servertime() -> str:
    return f"[{datetime.now().strftime("%H:%M:%S")}]"

import asyncio
import discord
import config
import time
import requests
import bot_instance
from utils.env_helper import insert_env, remove_env_key
from utils.core_helper import restart, error, log, warning

START_TIME: float | None = None

REMOTE_RELEASE_URL = "https://api.github.com/repos/JustinPhong/Cordmin-Discord-Bot/releases/latest"

def validate_config():
    if not config.BOT_TOKEN:
        key = insert_env("BOT_TOKEN",label="Bot Token")
        config.BOT_TOKEN = key
    
    if not config.GUILD_ID:
        key = insert_env("GUILD_ID",label="Guild ID")
        config.GUILD_ID = key

    if not config.APPLICATION_ID:
        key = insert_env("APPLICATION_ID",label="Application ID")
        config.APPLICATION_ID = key

def get_remote_version():
    try:
        response = requests.get(REMOTE_RELEASE_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("tag_name", "").lower(), data.get("html_url", "")
    except Exception as e:
        warning(f"Failed to check remote version", e)
        return None

async def main():
    global START_TIME
    try:
        remote_version, release_url = get_remote_version()
        if remote_version and remote_version != config.VERSION.lower():
            warning(f"New version available: {remote_version} {release_url} (current: {config.VERSION.lower()})")
    except Exception as e:
        pass
    while True:
        log(f"Cordmin {config.VERSION} initialising")
        START_TIME = time.monotonic()
        validate_config()
        bot = bot_instance.CordminBot() 
        bot.start_time = time.monotonic()
        try:
            await bot.start(config.BOT_TOKEN)
            return
        except (discord.LoginFailure, TypeError):
            remove_env_key("BOT_TOKEN")
            config.BOT_TOKEN = None
            if await restart("Invalid Bot Token"):
                continue
            else:
                break
        except Exception as e:
            error("Failed to initialise bot", e)
            break
        finally:
            if not bot.is_closed():
                await bot.close()
    log("Cordmin stopped")

asyncio.run(main())
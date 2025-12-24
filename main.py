import asyncio
import discord
import config
import time
import bot_instance
from utils.env_helper import insert_env, remove_env_key
from utils.core_helper import restart, error, log

START_TIME: float | None = None

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

async def main():
    global START_TIME
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
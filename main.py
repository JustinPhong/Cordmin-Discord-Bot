import asyncio
import signal
import discord
import os
import config
import time
from bot_instance import bot
from utils.env_helper import insert_env, remove_env_key
from utils.core_helper import restart, error, success, log
from discord.ext import commands
from discord import app_commands

START_TIME: float | None = None

@bot.event
async def on_ready():
    await init()
    guild_obj = discord.Object(id=int(config.GUILD_ID))
    bot.tree.copy_global_to(guild=guild_obj)
    await bot.tree.sync(guild=guild_obj)
    elapsed = time.monotonic() - START_TIME
    success(f"Cordmin started ({elapsed:.2f}s!)")

async def init():
    while True:
        try:
            guild = bot.get_guild(config.GUILD_ID)
            if guild is None:
                guild = await bot.fetch_guild(config.GUILD_ID)

            member = guild.get_member(bot.user.id)
            if member is None:
                member = await guild.fetch_member(bot.user.id)

            await member.edit(nick="Cordmin")
            return guild

        except discord.NotFound:
            remove_env_key("GUILD_ID")
            retry = await restart(f"Unknown Guild {config.GUILD_ID}")
            if retry:
                key = insert_env("GUILD_ID", label="Guild ID")
                config.GUILD_ID = key
                continue
            else:
                await bot.close()
                return None

        except Exception as e:
            error("Failed to connect to guild", e)
            await bot.close()
            return None

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
        try:
            await bot.start(config.BOT_TOKEN)
            break
        except (discord.LoginFailure, TypeError):
            remove_env_key("BOT_TOKEN")
            if await restart("Invalid Bot Token"):
                continue
        except Exception as e:
            error("Failed to initialise bot", e)
        finally:
            if not bot.is_closed():
                await bot.close()
            log("Cordmin stopped")
            break

asyncio.run(main())
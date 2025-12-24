import discord
import config
import time
from discord.ext import commands
from utils.core_helper import log, error, restart, success
from utils.env_helper import insert_env, remove_env_key

class CordminBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.start_time: float | None = None

    async def setup_hook(self):
        extensions = [
            "command.general",
            "command.admin",
            "listener.voice",
            "listener.reaction",
            "utils.server_helper"
        ]

        for ext in extensions:
            try:
                await self.load_extension(ext)
            except Exception as e:
                error(f"Failed to load {ext}", e)

        log("Cogs fully loaded")

    async def on_ready(self):
        await self.init()
        guild_obj = discord.Object(id=int(config.GUILD_ID))
        self.tree.copy_global_to(guild=guild_obj)
        await self.tree.sync(guild=guild_obj)
        elapsed = time.monotonic() - self.START_TIME
        success(f"Cordmin started ({elapsed:.2f}s!)")

    async def init(self):
        while True:
            try:
                guild = self.get_guild(config.GUILD_ID)
                if guild is None:
                    guild = await self.fetch_guild(config.GUILD_ID)

                member = guild.get_member(self.user.id)
                if member is None:
                    member = await guild.fetch_member(self.user.id)

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
                    await self.close()
                    return None

            except Exception as e:
                error("Failed to connect to guild", e)
                await self.close()
                return None
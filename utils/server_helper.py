import os
import time
import json
import config
import asyncio
import discord
from mcstatus import JavaServer
from discord.ext import commands
from discord import app_commands
from utils.discord_helper import load_json, save_json
from utils.core_helper import log, error, warning

class MCStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.loop())

    async def loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            data = load_json("servers.json")

            tasks = [asyncio.create_task(self.check_server(int(guild_id), cfg, data))for guild_id, cfg in data.items()]
            await asyncio.gather(*tasks, return_exceptions=True)

            save_json(data, "servers.json")
            await asyncio.sleep(config.CHECK_INTERVAL)

    async def check_server(self, guild_id, cfg, data):
        now = time.time()
        if cfg.get("cooldown_until", 0) > now:
            return
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, check_mc, cfg["ip"], cfg["port"])
            online = True
        except Exception:
            online = False
            result = None
        if config.LOG_MCSTATUS:
            log(f"{cfg['ip']}:{cfg['port']} - {cfg['last_status']}")
        if cfg.get("last_status") == online:
            return
        channel = self.bot.get_channel(cfg["channel_id"])
        if not channel:
            return
        message = None
        if cfg.get("message_id"):
            try:
                message = await channel.fetch_message(cfg["message_id"])
            except discord.NotFound:
                message = None
        if not online:
            cfg["last_status"] = False
            cfg["cooldown_until"] = now + config.COOLDOWN_SECONDS
            content = (
                f"🔴 **Server OFFLINE**\n"
                f"`{cfg['ip']}:{cfg['port']}`\n"
                f"Next check in {config.COOLDOWN_SECONDS // 60} minutes"
            )
        else:
            cfg["last_status"] = True
            cfg["cooldown_until"] = 0
            content = (
                f"🟢 **Server ONLINE**\n"
                f"`{cfg['ip']}:{cfg['port']}`\n"
                f"Players: {result['players']}/{result['max']}\n"
                f"Version: {result['version']}"
            )
        if message:
            await message.edit(content=content)
        else:
            msg = await channel.send(content)
            cfg["message_id"] = msg.id
        data[str(guild_id)] = cfg

def check_mc(ip, port):
    server = JavaServer.lookup(f"{ip}:{port}")
    status = server.status()
    return {
        "players": status.players.online,
        "max": status.players.max,
        "version": status.version.name
    }

class LogForwarder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    async def cog_load(self):
        self.bot.loop.create_task(self.start())

    async def start(self):
        await self.bot.wait_until_ready()
        data = load_json("servers.json")

        for guild_id, servers in data.items():
            for cfg in servers:
                log_channel_id = cfg.get("log_channel")
                log_dir = cfg.get("latest_log")

                if not log_channel_id or not log_dir:
                    continue

                log_path = os.path.join(log_dir, "latest.log")

                if not os.path.isfile(log_path):
                    warning(f"Log file not found: {log_path}")
                    continue

                key = f"{guild_id}:{log_path}"
                if key not in self.tasks:
                    self.tasks[key] = asyncio.create_task(
                        self.forward_logs(guild_id, log_channel_id, log_path)
                    )

    async def forward_logs(self, guild_id, log_channel_id, log_path):
        last_position = 0

        while not self.bot.is_closed():
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_position)
                    lines = f.readlines()
                    last_position = f.tell()

                if lines:
                    channel = self.bot.get_channel(log_channel_id)
                    if channel:
                        for line in lines:
                            await channel.send(line.rstrip())

            except Exception as e:
                error(f"Log read failed ({guild_id})", e)

            await asyncio.sleep(5)

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(MCStatus(bot))
        await bot.add_cog(LogForwarder(bot))
        log("MC status loaded")
    except Exception as e:
        error("Failed to load mc status", e)
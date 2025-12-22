import discord
from discord.ext import commands
import config
from utils.core_helper import log, error

class CordminBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            await self.load_extension("command.general")
        except Exception as e:
            error("Failed to load general", e)        
        try:
            await self.load_extension("command.admin")
        except Exception as e:
            error("Failed to load admin", e)        
        try:
            await self.load_extension("listener.voice")
        except Exception as e:
            error("Failed to load voice", e)        
        try:
            await self.load_extension("listener.reaction")
        except Exception as e:
            error("Failed to load reaction", e)        
        try:
            await self.load_extension("utils.server_helper")
        except Exception as e:
            error("Failed to server helper", e)    
        log("Cogs fully loaded")

bot = CordminBot()

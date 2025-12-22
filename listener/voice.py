import discord
import config
from discord.ext import commands
from utils.core_helper import log, error
from utils.discord_helper import load_json, save_json, remove_json

class VoiceListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self,member: discord.Member,before: discord.VoiceState,after: discord.VoiceState):
        if after.channel and after.channel.id == int(config.VOICE_TEMP_CHANNEL):
            guild = member.guild
            category = after.channel.category
            created_channel = await guild.create_voice_channel(name=f"{member.name}'s channel",category=category,user_limit=5)
            await member.move_to(created_channel)

        if before.channel and before.channel.name.endswith("'s channel"):
            if len(before.channel.members) == 0:
                await before.channel.delete()

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(VoiceListener(bot))
        log("Voice listener loaded")
    except Exception as e:
        error("Failed to load voice listener", e)

import discord
import config
from discord.ext import commands
from utils.core_helper import log, error
from utils.discord_helper import load_json, save_json, remove_json

class ReactionListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        if payload.message_id != config.NOTIFICATION_MSG_ID:
            return
        data = load_json()
        guild_id = str(payload.guild_id)
        if guild_id not in data:
            return
        emoji = str(payload.emoji)
        if emoji not in data[guild_id]:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            member = await guild.fetch_member(payload.user_id)
        role_id = data[guild_id][emoji]
        role = guild.get_role(role_id)
        if not role:
            return
        await member.add_roles(role, reason="Reaction role added")
        try:
            await member.send(f"You have been given {role.name}")
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.message_id != config.NOTIFICATION_MSG_ID:
            return
        data = load_json()
        guild_id = str(payload.guild_id)
        if guild_id not in data:
            return
        emoji = str(payload.emoji)
        if emoji not in data[guild_id]:
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return
        role_id = data[guild_id][emoji]
        role = guild.get_role(role_id)
        if not role:
            return
        await member.remove_roles(role, reason="Reaction role removed")

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(ReactionListener(bot))
        log("Reaction listener loaded")
    except Exception as e:
        error("Failed to load reaction listener", e)

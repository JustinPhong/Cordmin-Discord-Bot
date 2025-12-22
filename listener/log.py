import discord
import config
from discord.ext import commands
from utils.core_helper import log, error, servertime
from utils.discord_helper import load_json, save_json, remove_json

class LogListener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member == self.bot.user:
            return
        if config.ANNOUNCEMENT_CHANNEL:
            log_channel = self.bot.get_channel(config.ANNOUNCEMENT_CHANNEL)
            if log_channel:
                await log_channel.send(f"**{member.name}** left us")
        if config.LOG_CHANNEL:
            log_channel = self.bot.get_channel(config.LOG_CHANNEL)
            if log_channel:
                await log_channel.send(f"{servertime} {member.name} left the server")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member == self.bot.user:
            return
        if config.ANNOUNCEMENT_CHANNEL:
            log_channel = self.bot.get_channel(config.ANNOUNCEMENT_CHANNEL)
            if log_channel:
                await log_channel.send(f"<@{member.id}> welcome!")
        if config.LOG_CHANNEL:
            log_channel = self.bot.get_channel(config.LOG_CHANNEL)
            if log_channel:
                await log_channel.send(f"{servertime} {member.name} joined the server")

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.inviter == self.bot.user:
            return

        if config.LOG_CHANNEL:
            inviter_name = invite.inviter.name if invite.inviter else "Unknown"
            code = invite.code
            channel_name = invite.channel.name if invite.channel else "Unknown"
            uses = invite.uses
            max_uses = invite.max_uses
            temporary = invite.temporary
            log_channel = self.bot.get_channel(config.LOG_CHANNEL)
            if log_channel:
                await log_channel.send(f"{servertime} Invite created by {inviter_name}: https://discord.gg/{code}\nChannel: {channel_name}, Uses: {uses}/{max_uses}, Temporary: {temporary}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if config.LOG_CHANNEL:
            log_channel = self.bot.get_channel(config.LOG_CHANNEL)
            if log_channel:
                log_msg = f"{servertime} <@{message.author.id}> deleted a message in <#{message.channel.id}>\n>>> {message.content}"
                if message.attachments:
                    log_msg += "\nAttachments: " + ", ".join([a.url for a in message.attachments])
                await log_channel.send(log_msg)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author == self.bot.user:
            return
        before_content = before.content or "[No text content]"
        after_content = after.content or "[No text content]"
        if before.attachments:
            before_content += "\nAttachments: " + ", ".join(a.url for a in before.attachments)
        if after.attachments:
            after_content += "\nAttachments: " + ", ".join(a.url for a in after.attachments)
        log_channel = self.bot.get_channel(config.LOG_CHANNEL)
        if log_channel:
            log_msg = (f"{servertime} <@{before.author.id}> edited a message in <#{before.channel.id}>\n>>>**Before:**\n{before_content}\n**After:**\n{after_content}")
            await log_channel.send(log_msg)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(LogListener(bot))
        log("Log Listener loaded")
    except Exception as e:
        error("Failed to load log listener", e)

import config
import discord
from discord.ext import commands
from discord import app_commands
from utils.core_helper import log, error, warning
from utils.env_helper import insert_env, remove_env_key
from utils.discord_helper import load_json, save_json, remove_json
from gamercon_async import GameRCON,GameRCONBase64,ClientError,TimeoutError,InvalidPassword

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stop_cordmin", description="Stop Cordmin bot")
    @app_commands.default_permissions(administrator=True) 
    async def stop_cordmin(self, interaction: discord.Interaction):
        await interaction.response.send_message("Good bye!", ephemeral=True)
        if not self.bot.is_closed():
            await self.bot.close()
        log("Cordmin stopped")

    @app_commands.command(name="notification_add", description="Create a new notification")
    @app_commands.describe(emoji="The emoji users will react with (Unicode or custom)",tag_role="The role to assign when reacted")
    @app_commands.default_permissions(administrator=True)
    async def notification_add(self, interaction: discord.Interaction, emoji: str, tag_role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        try:
            data = load_json()
            guild_id = str(interaction.guild.id)
            if guild_id not in data:
                data[guild_id] = {}

            if emoji in data[guild_id]:
                return await interaction.followup.send(f"Emoji {emoji} is already used for role <@&{data[guild_id][emoji]}>",ephemeral=True)

            if tag_role.id in data[guild_id].values():
                existing_emoji = [em for em, role_id in data[guild_id].items() if role_id == tag_role.id][0]
                return await interaction.followup.send(f"Role {tag_role.name} is already assigned to emoji {existing_emoji}",ephemeral=True)

            data[guild_id][emoji] = tag_role.id
            save_json(data)

            guild = interaction.guild
            msg_content = "## Cordmin Notification🔔\nReact to subscribe to the notification!"
            for em, role_id in data[guild_id].items():
                role = guild.get_role(role_id)
                role_name = role.name if role else f"Unknown Role ({role_id})"
                msg_content += f"\n{em} : {role_name}"

            if not config.NOTIFICATION_MSG_ID:
                channel = interaction.channel
                sent_msg = await channel.send(msg_content)
                config.NOTIFICATION_MSG_ID = sent_msg.id
                config.NOTIFICATION_CHANNEL = channel.id
                insert_env("NOTIFICATION_MSG_ID", value=sent_msg.id)
                insert_env("NOTIFICATION_CHANNEL", value=channel.id)
            else:
                channel = await self.bot.fetch_channel(config.NOTIFICATION_CHANNEL)
                sent_msg = await channel.fetch_message(config.NOTIFICATION_MSG_ID)
                await sent_msg.edit(content=msg_content)
                
            for em, role_id in data[guild_id].items():
                await sent_msg.add_reaction(em)

            for reaction in sent_msg.reactions:
                async for user in reaction.users():
                    if user.id == self.bot.user.id:
                        if str(reaction.emoji) not in data[guild_id]:
                            await sent_msg.remove_reaction(reaction, self.bot.user)

            await interaction.followup.send("Notification added successfully", ephemeral=True)

        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="notification_remove",description="Remove a notification role")
    @app_commands.describe(tag_role="The role to remove notification")
    @app_commands.default_permissions(administrator=True)
    async def notification_remove(self,interaction: discord.Interaction,tag_role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        try:
            guild_id = str(interaction.guild.id)
            removed = remove_json(guild_id=guild_id, role_id=tag_role.id)
            if not removed:
                return await interaction.followup.send(f"Role {tag_role.name} is not registered",ephemeral=True)
            data = load_json()
            guild = interaction.guild
            msg_content = "## Cordmin Notification🔔\nReact to subscribe to the notification!"
            for em, role_id in data.get(guild_id, {}).items():
                role = guild.get_role(role_id)
                role_name = role.name if role else f"Unknown Role ({role_id})"
                msg_content += f"\n{em} : {role_name}"
            channel = await self.bot.fetch_channel(config.NOTIFICATION_CHANNEL)
            sent_msg = await channel.fetch_message(config.NOTIFICATION_MSG_ID)
            await sent_msg.edit(content=msg_content)
            valid_emojis = set(data.get(guild_id, {}).keys())
            for reaction in sent_msg.reactions:
                emoji_str = str(reaction.emoji)
                if emoji_str not in valid_emojis:
                    await sent_msg.remove_reaction(reaction.emoji, self.bot.user)

            await interaction.followup.send(f"Removed notification for role {tag_role.name}",ephemeral=True)

        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}",ephemeral=True)

    @app_commands.command(name="voice_hub_create",description="Create a temporary voice channel hub")
    @app_commands.default_permissions(administrator=True)
    async def voice_hub_create(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            guild = interaction.guild
            if config.VOICE_TEMP_CHANNEL:
                old_channel = guild.get_channel(int(config.VOICE_TEMP_CHANNEL))
                if old_channel:
                    await old_channel.delete()
            if config.VOICE_TEMP_CATEGORY:
                old_category = guild.get_channel(int(config.VOICE_TEMP_CATEGORY))
                if old_category:
                    await old_category.delete()
            category = await guild.create_category("Cordmin Hub")
            config.VOICE_TEMP_CATEGORY = category.id
            insert_env("VOICE_TEMP_CATEGORY", value=category.id)
            voice = await guild.create_voice_channel("Click to create",category=category)
            config.VOICE_TEMP_CHANNEL = voice.id
            insert_env("VOICE_TEMP_CHANNEL", value=voice.id)
            await interaction.followup.send("Voice hub created successfully!",ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}",ephemeral=True)

    @app_commands.command(name="config", description="Config channel")
    @app_commands.choices(config=[app_commands.Choice(name="Log", value="Log"),app_commands.Choice(name="Announcement", value="Announcement")])
    @app_commands.default_permissions(administrator=True)
    async def add_log(self, interaction: discord.Interaction, config: str, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        try:
            if config == "Log":
                insert_env("LOG_CHANNEL", channel.id)
                config.LOG_CHANNEL = channel.id
                await interaction.followup.send(f"Log channel updated", ephemeral=True)
            elif config == "Announcement":
                insert_env("ANNOUNCEMENT_CHANNEL", channel.id)
                config.ANNOUNCEMENT_CHANNEL = channel.id
                await interaction.followup.send(f"Announcement channel updated", ephemeral=True)
            else:
                await interaction.followup.send(f"Unknown config option", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="config_remove", description="Remove config channel")
    @app_commands.choices(config=[app_commands.Choice(name="Log", value="Log"),app_commands.Choice(name="Announcement", value="Announcement")])
    @app_commands.default_permissions(administrator=True)
    async def config_remove(self, interaction: discord.Interaction, config: str):
        await interaction.response.defer(ephemeral=True)
        try:
            if config == "Log":
                remove_env_key("LOG_CHANNEL")
                config.LOG_CHANNEL = None
                await interaction.followup.send(f"Log channel removed", ephemeral=True)
            elif config == "Announcement":
                remove_env_key("ANNOUNCEMENT_CHANNEL")
                config.ANNOUNCEMENT_CHANNEL = None
                await interaction.followup.send(f"Announcement channel removed", ephemeral=True)
            else:
                await interaction.followup.send(f"Unknown config option", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="rcon", description="Send an RCON command to the game server")
    @app_commands.default_permissions(administrator=True)
    async def rcon(self, interaction: discord.Interaction, port: int, password: str, command: str, ip: str|None="127.0.0.1"):
        await interaction.response.defer(ephemeral=True)
        try:
            async with GameRCON(ip, port, password) as rcon:
                response = await rcon.send(command)
            await interaction.followup.send(f"RCON Response:\n```\n{response}\n```", ephemeral=True)
        except InvalidPassword:
            await interaction.followup.send("Invalid RCON password!", ephemeral=True)
        except TimeoutError:
            await interaction.followup.send("RCON connection timed out", ephemeral=True)
        except ClientError as e:
            await interaction.followup.send(f"Client error: {e}", ephemeral=True)
        except Exception as e:
            warning("Failed to run",e)
            await interaction.followup.send(f"Failed to run: {type(e).__name__}: {e}", ephemeral=True)

    @app_commands.command(name="message_delete",description="Clear messages from a channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(number="Number of messages to delete or 'all' to clear everything")
    async def message_delete(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer(ephemeral=True)
        try:
            if number < 1 or number > 100:
                return await interaction.followup.send("Please specify a number between 1 and 100.", ephemeral=True)
            deleted = await interaction.channel.purge(limit=number)
            await interaction.followup.send(f"Successfully cleared {len(deleted)} messages!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to delete messages in that channel", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="message_send", description="Send a message")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(text_to_send="Text to send",image_file="Optional image attachment")
    async def message_send(self,interaction: discord.Interaction,text_to_send: str,image_file: discord.Attachment | None = None):
        await interaction.response.defer(ephemeral=True)
        channel = interaction.channel
        try:
            if image_file:
                await channel.send(content=text_to_send, file=await image_file.to_file())
            else:
                await channel.send(content=text_to_send)
            await interaction.followup.send("Message sent successfully!", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="message_copy",description="Copy a message")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(fromchannel="Copy from channel",tochannel="Paste to channel",frommessage="Message ID")
    async def message_copy(self,interaction: discord.Interaction,fromchannel: discord.TextChannel,tochannel: discord.TextChannel,frommessage: str):
        await interaction.response.defer(ephemeral=True)
        try:
            message = await fromchannel.fetch_message(int(frommessage))
            files = []
            for attachment in message.attachments:
                try:
                    files.append(await attachment.to_file())
                except Exception as e:
                    warning("Failed to convert attachment", e)
            embeds = message.embeds if message.embeds else None
            await tochannel.send(content=message.content or None, files=files, embeds=embeds)
            await interaction.followup.send(f"Message pasted to {tochannel.mention}",ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send("Message not found. Make sure the ID and channel are correct",ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to access that channel or message",ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="message_edit", description="Edit a message")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(edimessageid="Original message ID",text_to_send="New text to send",text_id_to_send="New text copy from message ID", fromchannel="Copy from channel")
    async def message_edit(self,interaction: discord.Interaction,edimessageid: int,text_to_send: str | None = None,text_id_to_send: int | None = None,fromchannel: discord.TextChannel | None = None):
        await interaction.response.defer(ephemeral=True)
        try:
            channel = fromchannel or interaction.channel
            message = await channel.fetch_message(int(edimessageid))
            if text_id_to_send and fromchannel:
                source_message = await fromchannel.fetch_message(int(text_id_to_send))
                new_content = source_message.content
            elif text_to_send:
                new_content = text_to_send
            else:
                await interaction.followup.send("No content provided to edit the message with", ephemeral=True)
                return
            await message.edit(content=new_content)
            await interaction.followup.send(f"Message edited successfully in {channel.mention}", ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send("Message not found. Make sure the ID is correct", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to edit that message", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="message_react", description="React to a message")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(message_id="Message ID to react",emojis="Unicode or custom, support multiple reactions separated by ','")
    async def message_react(self,interaction: discord.Interaction,message_id: int,emojis: str,channel: discord.TextChannel | None = None):
        await interaction.response.defer(ephemeral=True)
        target_channel = channel or interaction.channel
        try:
            message = await target_channel.fetch_message(message_id)
            emoji_list = [e.strip() for e in emojis.split(",") if e.strip()]
            added = []
            failed = []
            for emoji in emoji_list:
                try:
                    await message.add_reaction(emoji)
                    added.append(emoji)
                except discord.HTTPException:
                    failed.append(emoji)
            response = ""
            if added:
                response += f"Reactions added: {', '.join(added)}.\n"
            if failed:
                response += f"Failed to add: {', '.join(failed)}"
            await interaction.followup.send(response, ephemeral=True)
        except discord.NotFound:
            await interaction.followup.send("Message not found. Make sure the ID is correct", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to react to that message", ephemeral=True)
        except Exception as e:
            warning("Failed to run", e)
            await interaction.followup.send(f"Failed to run: {e}", ephemeral=True)

    @app_commands.command(name="server_mc_add",description="Start watching a Minecraft server status and log to channel")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(ip="Server IP or domain",port="Server port (default 25565)",channel="Channel to send status updates",log_channel="Optional log channel",log_file_path="FIle path to Minecraft\\Logs")
    async def server_mc_add(self,interaction: discord.Interaction,ip: str,channel: discord.TextChannel,port: int = 25565,log_channel: discord.TextChannel | None = None, log_file_path: str | None = None):
        await interaction.response.defer(ephemeral=True)
        data = load_json("servers.json")
        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            data[guild_id] = []
        old_entries = [s for s in data[guild_id] if s["ip"] == ip and s["port"] == port]
        for entry in old_entries:
            data[guild_id].remove(entry)
        server_entry = {"ip": ip,"port": port,"channel_id": channel.id,"log_channel": log_channel.id if log_channel else None,"latest_log": log_file_path if log_file_path else None,"message_id": None,"last_status": None,"cooldown_until": 0}
        data[guild_id].append(server_entry)
        save_json(data, "servers.json")
        await interaction.followup.send(f"Now watching {ip}:{port}. Updates will be sent to {channel.mention}",ephemeral=True)


async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(AdminCog(bot))
        log("Admin command loaded")
    except Exception as e:
        error("Failed to load admin command", e)
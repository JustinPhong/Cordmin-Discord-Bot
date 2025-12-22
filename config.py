import discord
import os
from dotenv import load_dotenv

load_dotenv(override=True)

VERSION = 'V1.0'
GUILD_ID = os.getenv("GUILD_ID")
APPLICATION_ID = os.getenv("APPLICATION_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTIFICATION_MSG_ID = os.getenv("NOTIFICATION_MSG_ID")
NOTIFICATION_CHANNEL = os.getenv("NOTIFICATION_CHANNEL")
VOICE_TEMP_CATEGORY = os.getenv("VOICE_TEMP_CATEGORY")
VOICE_TEMP_CHANNEL= os.getenv("VOICE_TEMP_CHANNEL")
ANNOUNCEMENT_CHANNEL = os.getenv("ANNOUNCEMENT_CHANNEL")
LOG_CHANNEL= os.getenv("LOG_CHANNEL")

intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True

LOG_MCSTATUS = False
COOLDOWN_SECONDS = 300
CHECK_INTERVAL = 60

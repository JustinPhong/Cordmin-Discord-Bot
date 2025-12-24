import discord
import toml
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
VOICE_TEMP_CHANNEL = os.getenv("VOICE_TEMP_CHANNEL")
ANNOUNCEMENT_CHANNEL = os.getenv("ANNOUNCEMENT_CHANNEL")
LOG_CHANNEL = os.getenv("LOG_CHANNEL")

intents = discord.Intents.all()
intents.message_content = True
intents.guilds = True
intents.members = True

USER_CONFIG_PATH = "Config"

if os.path.isfile(USER_CONFIG_PATH):
    with open(USER_CONFIG_PATH, "r") as f:
        user_config = toml.load(f)
else:
    default_config = """LOG_MCSTATUS = false
#Cooldown period if server is offline, minimum 1 second
COOLDOWN_SECONDS = 300
#Check server status interval in seconds, minimum 1 second
CHECK_INTERVAL = 60
LOG_FILE = true"""
    with open(USER_CONFIG_PATH, "w") as f:
        f.write(default_config)
        user_config = toml.loads(default_config)

LOG_MCSTATUS = user_config.get("LOG_MCSTATUS", False)
COOLDOWN_SECONDS = max(user_config.get("COOLDOWN_SECONDS", 1), 1)
CHECK_INTERVAL = max(user_config.get("CHECK_INTERVAL", 1), 1)
LOG_FILE = user_config.get("LOG_FILE", True)
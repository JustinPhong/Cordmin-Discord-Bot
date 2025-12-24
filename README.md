# Cordmin Discord Bot

A modular, feature-rich Discord bot built with **discord.py**.  
Cordmin provides Minecraft server monitoring, reaction roles, logging, voice hub automation, and powerful administrator slash commands — all designed with persistence and extensibility in mind.

---

## 🚀 Features

### 🎮 Minecraft Server Monitoring
- Monitor **Minecraft Java Edition** servers
- Live online/offline detection
- Player count & version display
- Persistent status message (auto edit instead of spam)
- Auto-reconnect cooldown to prevent notification spam
- Multi-server & multi-guild support

### ⌨️ RCON
- Support remote command to game servers

### 🔔 Reaction Roles
- Assign roles via emoji reactions
- Supports Unicode & custom emojis
- Add/remove roles dynamically
- Persistent storage using JSON

### 🧾 Logging System
Logs important server activities:
- Member join / leave
- Message edits & deletions
- Invite creation
- Optional announcement & log channels

### 🎧 Voice Hub System
- Auto-create temporary voice channels
- “Click to Create” hub channel
- Auto-delete empty channels
- Clean & scalable voice management

### 🛠 Admin Slash Commands
- Message send / copy / edit / delete
- Reaction management
- Server configuration commands
- Permission-protected admin tools

---

## 🧱 Tech Stack

- **Python 3.10+**
- **discord.py (app_commands / slash commands)**
- **asyncio**
- **mcstatus** (Minecraft server queries)
- **JSON-based persistence**
- Modular **Cog-based architecture**

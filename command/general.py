import discord
import random
import asyncio
from discord.ext import commands
from discord import app_commands
from utils.core_helper import log, error

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="are_you_alive", description="Check Cordmin Status")
    async def are_you_alive(self, interaction: discord.Interaction):
        await interaction.response.send_message("I'm Alive!", ephemeral=True)

    @app_commands.command(name="spin", description="Spin a wheel")
    @app_commands.describe(spin_item="Support multiple items separated by ','")
    async def SpinAnItem(self, interaction: discord.Interaction, spin_item: str):
        items = [e.strip() for e in spin_item.split(",") if e.strip()]
        if not items:
            return await interaction.response.send_message("You need at least one item to spin!", ephemeral=True)
        await interaction.response.send_message("Spinning the wheel... 🎡")
        for i in ["3!", "2!", "1!"]:
            await asyncio.sleep(1)
            await interaction.edit_original_response(content=i)
        winner = random.choice(items)
        await asyncio.sleep(0.5)
        await interaction.edit_original_response(content=f"🎉 The winner goes to: **{winner}**\nSpin Items: {', '.join(items)}")

async def setup(bot: commands.Bot):
    try:
        await bot.add_cog(GeneralCog(bot))
        log("General command loaded")
    except Exception as e:
        error("Failed to load general command", e)
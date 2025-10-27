from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)

class SetupCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(description="Create roles/channels/categories")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, interaction: discord.Interaction):
        g = interaction.guild
        await interaction.response.defer(ephemeral=True)
        # roles
        for name in CONFIG["roles"].values():
            if not discord.utils.get(g.roles, name=name):
                await g.create_role(name=name, mentionable=True)
        # category + channels
        cat = discord.utils.get(g.categories, name=CONFIG["categories"]["tickets"]) or await g.create_category(CONFIG["categories"]["tickets"])
        for ch in CONFIG["channels"].values():
            if not discord.utils.get(g.text_channels, name=ch):
                await g.create_text_channel(ch)
        await interaction.followup.send("Setup complete ✅", ephemeral=True)

async def setup(bot): await bot.add_cog(SetupCog(bot))

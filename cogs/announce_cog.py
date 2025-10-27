from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
class AnnounceCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="Announce a release")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def announcebot(self, interaction: discord.Interaction, title: str, description: str):
        e = discord.Embed(title=title, description=description, color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"]); await interaction.response.send_message(embed=e)
async def setup(bot): await bot.add_cog(AnnounceCog(bot))

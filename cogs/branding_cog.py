from __future__ import annotations
import discord, json, random
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
class BrandingCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="About BotForge")
    async def about(self, interaction: discord.Interaction):
        e = discord.Embed(title="BotForge", description="Custom bots • Clean installs • Fast support", color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"]); await interaction.response.send_message(embed=e)
async def setup(bot): await bot.add_cog(BrandingCog(bot))

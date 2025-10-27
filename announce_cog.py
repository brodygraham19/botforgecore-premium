from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

class AnnounceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Announce a new bot or update")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def announcebot(self, interaction: discord.Interaction, title: str, description: str):
        news_ch = discord.utils.get(interaction.guild.text_channels, name=CONFIG["channels"]["news"])
        if not news_ch:
            news_ch = interaction.channel
        e = discord.Embed(title=title, description=description, color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"])
        await news_ch.send(embed=e)
        await interaction.response.send_message(f"Announcement sent to {news_ch.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AnnounceCog(bot))

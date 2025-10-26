from __future__ import annotations
import discord, json, random
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)
ACCENT = int(CONFIG["accent_color_hex"].replace("#",""),16)

QUOTES = [
    "Forge your future. 🔥",
    "Build fast, ship clean.",
    "Bots don't sleep — they ship.",
    "Strong code, stronger community."
]

class BrandingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="About BotForge")
    async def about(self, interaction: discord.Interaction):
        e = discord.Embed(title="BotForge", description="Custom bots • Clean installs • Fast support", color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"])
        e.add_field(name="What we do", value="Stock bots, ticket systems, verification, custom automation.")
        e.add_field(name="How to order", value="Use `/listbots` then `/order` to open a ticket.")
        await interaction.response.send_message(embed=e)

    @app_commands.command(description="Show the theme colors")
    async def theme(self, interaction: discord.Interaction):
        e = discord.Embed(title="Theme", description=f"Primary: `{CONFIG['theme_color_hex']}` • Accent: `{CONFIG['accent_color_hex']}`", color=ACCENT)
        await interaction.response.send_message(embed=e)

    @app_commands.command(description="Post the BotForge logo")
    async def logo(self, interaction: discord.Interaction):
        e = discord.Embed(color=COLOR)
        e.set_image(url=CONFIG["logo_url"])
        await interaction.response.send_message(embed=e)

    @app_commands.command(description="Motivate the server")
    async def motivate(self, interaction: discord.Interaction):
        await interaction.response.send_message(random.choice(QUALITY_QUOTES) if (QUALITY_QUOTES:=QUOTES) else "Forge your future. 🔥")

    @app_commands.command(description="Random tech/Discord fact or quote")
    async def funfact(self, interaction: discord.Interaction):
        facts = [
            "Discord slash commands require syncing when code updates.",
            "Permissions overwrite in channels can hide content from everyone except roles you choose.",
            "Buttons and modals make your bot feel premium."
        ]
        await interaction.response.send_message(random.choice(facts))

async def setup(bot: commands.Bot):
    await bot.add_cog(BrandingCog(bot))

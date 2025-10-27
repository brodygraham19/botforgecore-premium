from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)

class VerifyCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(description="Get the Verified role")
    async def verify(self, interaction: discord.Interaction):
        role_name = CONFIG["roles"]["verified"]
        role = discord.utils.get(interaction.guild.roles, name=role_name) or await interaction.guild.create_role(name=role_name, mentionable=True)
        if role in interaction.user.roles:
            return await interaction.response.send_message("You're already verified ✅", ephemeral=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("You’re verified! 🎉", ephemeral=True)

async def setup(bot): await bot.add_cog(VerifyCog(bot))

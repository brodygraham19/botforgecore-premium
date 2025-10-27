from __future__ import annotations
import discord, json, os
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
class ModerationCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str="—"):
        await member.kick(reason=reason); await interaction.response.send_message(f"Kicked {member}.", ephemeral=True)
async def setup(bot): await bot.add_cog(ModerationCog(bot))

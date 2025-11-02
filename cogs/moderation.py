
import discord, os
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason"):
        await interaction.guild.ban(user, reason=reason)
        await interaction.response.send_message(f"Banned {user}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))

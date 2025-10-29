from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

MIDNIGHT = 0x0f172a

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Delete a number of messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 200]):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted **{len(deleted)}** messages.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member for X minutes")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int,1,40320], reason: str=None):
        await member.timeout(timedelta(minutes=minutes), reason=reason or "Timed out")
        await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes} minutes.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        await member.kick(reason=reason or "Kicked")
        await interaction.response.send_message(f"👢 Kicked {member}")

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str=None):
        await member.ban(reason=reason or "Banned")
        await interaction.response.send_message(f"🔨 Banned {member}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))

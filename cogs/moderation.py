import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

def default_perms():
    return app_commands.default_permissions(manage_guild=True)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Clear a number of recent messages in this channel.")
    @default_perms()
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    @app_commands.describe(amount="How many messages to remove (1-100)")
    async def clear(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await interaction.channel.purge(limit=amount+1)  # type: ignore
        await interaction.followup.send(f"🧹 Removed {len(deleted)-1} messages.", ephemeral=True)

    @app_commands.command(description="Timeout a member for N minutes with a reason.")
    @default_perms()
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @app_commands.describe(member="Member to timeout", minutes="Minutes (1-10080)", reason="Why?")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int,1,10080], reason: Optional[str]=None):
        duration = discord.utils.utcnow() + discord.timedelta(minutes=int(minutes))
        await member.timeout(until=duration, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes}m. Reason: {reason or '—'}", ephemeral=True)

    @app_commands.command(description="Kick a member.")
    @default_perms()
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str]=None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.mention}. Reason: {reason or '—'}", ephemeral=True)

    @app_commands.command(description="Ban a member.")
    @default_perms()
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str]=None):
        await member.ban(reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"🔨 Banned {member.mention}. Reason: {reason or '—'}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))

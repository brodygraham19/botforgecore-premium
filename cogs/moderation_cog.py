
# cogs/moderation_cog.py
import discord
from discord import app_commands
from discord.ext import commands

def staff_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_guild
    return app_commands.check(predicate)

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Delete N recent messages (max 200).")
    @staff_only()
    async def purge(self, interaction: discord.Interaction, amount: int):
        amount = max(1, min(200, amount))
        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member for X minutes.")
    @staff_only()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str | None = None):
        dur = discord.utils.utcnow() + discord.timedelta(minutes=max(1, minutes))
        await member.timeout(dur, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes}m.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member.")
    @staff_only()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.mention}.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member.")
    @staff_only()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned {member.mention}.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))

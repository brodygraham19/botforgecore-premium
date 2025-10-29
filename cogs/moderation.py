
import discord
from discord import app_commands
from discord.ext import commands

def mod_only():
    return app_commands.checks.has_permissions(manage_messages=True)

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Delete a number of recent messages")
    @app_commands.describe(amount="How many messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("Pick 1-100.", ephemeral=True)
            return
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member for X minutes")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str | None = None):
        try:
            await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes), reason=reason)
            await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes}m.")
        except Exception as e:
            await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member}")

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.ban(reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"🔨 Banned {member}")

    @app_commands.command(name="mute", description="Server mute a member in voice")
    @app_commands.checks.has_permissions(mute_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        if member.voice and member.voice.channel:
            await member.edit(mute=True)
            await interaction.response.send_message(f"🔇 Muted {member.display_name}")
        else:
            await interaction.response.send_message("User is not in voice.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))

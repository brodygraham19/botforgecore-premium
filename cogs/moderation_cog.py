
# cogs/moderation_cog.py
import discord
from discord import app_commands
from discord.ext import commands

BRAND_COLOR = discord.Color(0x0B1220)
WARNINGS: dict[int, list[str]] = {}  # {user_id: [reasons]}

def staff_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_guild
    return app_commands.check(predicate)

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staff_only()
    @app_commands.command(name="clear", description="Delete N recent messages (max 200).")
    async def clear(self, interaction: discord.Interaction, amount: int):
        amount = max(1, min(200, amount))
        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="timeout", description="Timeout a member for X minutes.")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str | None = None):
        dur = discord.utils.utcnow() + discord.timedelta(minutes=max(1, minutes))
        await member.timeout(dur, reason=reason)
        await interaction.response.send_message(f"⏳ {member.mention} timed out for {minutes}m.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="kick", description="Kick a member.")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 Kicked {member.mention}.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="ban", description="Ban a member.")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 Banned {member.mention}.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="warn", description="Warn a member (stored in memory).")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        WARNINGS.setdefault(member.id, []).append(reason)
        await interaction.response.send_message(f"⚠️ {member.mention} warned: {reason}", ephemeral=True)

    @staff_only()
    @app_commands.command(name="warnings", description="Show a member's warnings (session memory).")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member):
        items = WARNINGS.get(member.id, [])
        if not items:
            await interaction.response.send_message("✅ No warnings.", ephemeral=True); return
        await interaction.response.send_message("⚠️ Warnings:\n- " + "\n- ".join(items), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))


import discord, os, json, pathlib
from discord.ext import commands
from discord import app_commands

LOGS_CHANNEL_ID = os.getenv("LOGS_CHANNEL_ID")
WARN_FILE = pathlib.Path("data/warnings.json")
WARN_FILE.parent.mkdir(parents=True, exist_ok=True)
if not WARN_FILE.exists(): WARN_FILE.write_text("{}")

def mod_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        staff_role_id = os.getenv("STAFF_ROLE_ID")
        if staff_role_id and interaction.user.get_role(int(staff_role_id)):
            return True
        return interaction.user.guild_permissions.manage_guild
    return app_commands.check(predicate)

async def send_log(guild: discord.Guild, embed: discord.Embed):
    try:
        if LOGS_CHANNEL_ID and LOGS_CHANNEL_ID.isdigit():
            ch = guild.get_channel(int(LOGS_CHANNEL_ID))
            if ch: await ch.send(embed=embed)
    except Exception: pass

class Moderation(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="ban", description="Ban a user")
    @mod_only()
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason provided"):
        await interaction.guild.ban(user, reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"🔨 Banned {user} | {reason}")
        await send_log(interaction.guild, discord.Embed(description=f"🔨 **Ban:** {user} | {reason}", color=0x992d22))

    @app_commands.command(name="kick", description="Kick a user")
    @mod_only()
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason provided"):
        await interaction.guild.kick(user, reason=reason)
        await interaction.response.send_message(f"👢 Kicked {user} | {reason}")
        await send_log(interaction.guild, discord.Embed(description=f"👢 **Kick:** {user} | {reason}", color=0x992d22))

    @app_commands.command(name="mute", description="Timeout a user in minutes")
    @mod_only()
    async def mute(self, interaction: discord.Interaction, user: discord.Member, minutes: int, reason: str=""):
        until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await user.timeout(until, reason=reason or "Timeout")
        await interaction.response.send_message(f"⛔ Timed out {user} for {minutes}m.")
        await send_log(interaction.guild, discord.Embed(description=f"⛔ **Timeout:** {user} {minutes}m", color=0xf1c40f))

    @app_commands.command(name="unmute", description="Remove timeout")
    @mod_only()
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        await user.timeout(None)
        await interaction.response.send_message(f"✅ Unmuted {user}")

    @app_commands.command(name="clear", description="Delete a number of messages")
    @mod_only()
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(name="warn", description="Warn a user")
    @mod_only()
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        data = json.loads(WARN_FILE.read_text())
        data.setdefault(str(user.id), []).append({"by": interaction.user.id, "reason": reason})
        WARN_FILE.write_text(json.dumps(data, indent=2))
        await interaction.response.send_message(f"⚠️ Warned {user}: {reason}")
        await send_log(interaction.guild, discord.Embed(description=f"⚠️ **Warn:** {user} | {reason}", color=0xf1c40f))

    @app_commands.command(name="warnings", description="List warnings for a user")
    @mod_only()
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        data = json.loads(WARN_FILE.read_text())
        warns = data.get(str(user.id), [])
        if not warns:
            return await interaction.response.send_message("✅ No warnings.", ephemeral=True)
        desc = "\n".join([f"• {w['reason']} (by <@{w['by']}>)" for w in warns])
        await interaction.response.send_message(embed=discord.Embed(title=f"Warnings for {user}", description=desc, color=0x2b2d31), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

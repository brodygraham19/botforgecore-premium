from __future__ import annotations
import discord, json, asyncio, os
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

WARNS_FILE = "data/warns.json"

def load_warns():
    import json
    if not os.path.exists(WARNS_FILE):
        return {}
    with open(WARNS_FILE,"r") as f:
        return json.load(f)

def save_warns(data):
    import json
    with open(WARNS_FILE,"w") as f:
        json.dump(data, f, indent=2)

class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Warn a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        data = load_warns()
        user_warnings = data.get(str(member.id), [])
        user_warnings.append({"by": interaction.user.id, "reason": reason})
        data[str(member.id)] = user_warnings
        save_warns(data)

        logs_name = CONFIG["channels"]["logs"]
        logs = discord.utils.get(interaction.guild.text_channels, name=logs_name)
        if logs:
            await logs.send(f"⚠️ {member.mention} warned by {interaction.user.mention}: **{reason}**")
        await interaction.response.send_message(f"Warned {member.mention}.", ephemeral=True)

    @app_commands.command(description="View warnings for a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, member: discord.Member):
        data = load_warns()
        wl = data.get(str(member.id), [])
        if not wl:
            await interaction.response.send_message("No warnings found.", ephemeral=True)
            return
        msg = "\n".join([f"{i+1}. {w['reason']}" for i, w in enumerate(wl)])
        await interaction.response.send_message(f"Warnings for {member.mention}:\n{msg}", ephemeral=True)

    @app_commands.command(description="Purge last N messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int = 20):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Purged {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member}.", ephemeral=True)

    @app_commands.command(description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        await interaction.guild.ban(member, reason=reason)
        await interaction.response.send_message(f"Banned {member}.", ephemeral=True)

    @app_commands.command(description="Unban by user ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: int):
        user = await self.bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"Unbanned {user}.", ephemeral=True)

    @app_commands.command(description="Timeout (mute) a member in minutes")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: str = "—"):
        until = discord.utils.utcnow() + discord.utils.timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        await interaction.response.send_message(f"Timed out {member} for {minutes} minutes.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))

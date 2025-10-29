
# cogs/admin_tools_cog.py
import discord
from discord import app_commands
from discord.ext import commands

BRAND_COLOR = discord.Color(0x0B1220)

def staff_only():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_channels
    return app_commands.check(predicate)

class AdminToolsCog(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    @staff_only()
    @app_commands.command(name="announce", description="Send an announcement embed to a channel.")
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, message: str):
        emb = discord.Embed(title=title, description=message, color=BRAND_COLOR)
        await channel.send(embed=emb)
        await interaction.response.send_message(f"✅ Sent to {channel.mention}", ephemeral=True)

    @staff_only()
    @app_commands.command(name="slowmode", description="Set slowmode (seconds) on this channel.")
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        seconds = max(0, min(21600, seconds))
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"🐢 Slowmode set to {seconds}s.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="lock", description="Lock this channel (prevent @everyone from sending).")
    async def lock(self, interaction: discord.Interaction):
        overwrites = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        await interaction.response.send_message("🔒 Channel locked.", ephemeral=True)

    @staff_only()
    @app_commands.command(name="unlock", description="Unlock this channel.")
    async def unlock(self, interaction: discord.Interaction):
        overwrites = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrites.send_messages = None  # reset to default
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrites)
        await interaction.response.send_message("🔓 Channel unlocked.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminToolsCog(bot))

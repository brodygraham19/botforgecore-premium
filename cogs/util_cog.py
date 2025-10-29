
# cogs/util_cog.py
import platform, time
import discord
from discord import app_commands
from discord.ext import commands

class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_ts = time.time()

    @app_commands.command(name="ping", description="Latency check.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! {round(self.bot.latency*1000)}ms", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Basic server info.")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        if not g:
            await interaction.response.send_message("Use this in a server.", ephemeral=True); return
        embed = discord.Embed(title=f"{g.name}", description="Server info", color=discord.Color.blurple())
        embed.add_field(name="Members", value=g.member_count)
        embed.add_field(name="Channels", value=len(g.channels))
        embed.add_field(name="Owner", value=g.owner.mention if g.owner else "Unknown")
        embed.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show a user's avatar.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="say", description="Make the bot say something (staff only).")
    @app_commands.describe(message="What should I say?")
    async def say(self, interaction: discord.Interaction, message: str):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Need Manage Messages.", ephemeral=True); return
        await interaction.response.send_message("✅ Sent.", ephemeral=True)
        await interaction.channel.send(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilCog(bot))

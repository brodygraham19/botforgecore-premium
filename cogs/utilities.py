from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

class Utilities(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    @app_commands.command(name="ping", description="Latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 {round(self.bot.latency*1000)} ms", ephemeral=True)

    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None=None):
        user = user or interaction.user
        e = discord.Embed(title=f"{user}", colour=discord.Colour.dark_embed())
        if user.display_avatar: e.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="userinfo", description="User info")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member | None=None):
        m = user or interaction.user  # type: ignore
        e = discord.Embed(title=f"User Info — {m}", colour=discord.Colour.dark_embed())
        e.add_field(name="ID", value=m.id)
        if isinstance(m, discord.Member) and m.joined_at: e.add_field(name="Joined", value=discord.utils.format_dt(m.joined_at, "R"))
        e.add_field(name="Created", value=discord.utils.format_dt(m.created_at, "R"))
        if isinstance(m, discord.Member) and m.display_avatar: e.set_thumbnail(url=m.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="serverinfo", description="Server info")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        e = discord.Embed(title=g.name, description=f"ID: {g.id}", colour=discord.Colour.dark_embed())
        e.add_field(name="Members", value=g.member_count)
        if g.icon: e.set_thumbnail(url=g.icon.url)
        await interaction.response.send_message(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utilities(bot))

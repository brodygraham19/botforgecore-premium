
import random
import discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! `{round(self.bot.latency*1000)} ms`")

    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member):
        e = discord.Embed(title=f"{user.display_name}'s avatar", color=0x0a192f)
        e.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="user", description="User info")
    async def user(self, interaction: discord.Interaction, user: discord.Member):
        e = discord.Embed(title=f"User Info — {user}", color=0x0a192f)
        e.add_field(name="ID", value=user.id, inline=True)
        e.add_field(name="Joined", value=discord.utils.format_dt(user.joined_at, "R"), inline=True)
        e.add_field(name="Account", value=discord.utils.format_dt(user.created_at, "R"), inline=True)
        e.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="server", description="Server info")
    async def server(self, interaction: discord.Interaction):
        g = interaction.guild
        e = discord.Embed(title=f"{g.name}", color=0x0a192f)
        e.add_field(name="Members", value=g.member_count)
        e.add_field(name="ID", value=g.id)
        if g.icon:
            e.set_thumbnail(url=g.icon.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="roleinfo", description="Info about a role")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        e = discord.Embed(title=f"Role: {role.name}", color=role.color or 0x0a192f)
        e.add_field(name="ID", value=role.id)
        e.add_field(name="Members", value=len(role.members))
        e.add_field(name="Mentionable", value=role.mentionable)
        await interaction.response.send_message(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))

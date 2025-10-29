from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! `{round(self.bot.latency*1000)}ms`")

    @app_commands.command(name="avatar", description="Show a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.User=None):
        user = user or interaction.user
        emb = discord.Embed(title=f"{user}'s avatar", color=discord.Color.dark_embed())
        if user.avatar:
            emb.set_image(url=user.avatar.url)
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="server", description="Server info")
    async def server(self, interaction: discord.Interaction):
        g = interaction.guild
        emb = discord.Embed(title=g.name, description=f"Members: {g.member_count}", color=discord.Color.dark_embed())
        await interaction.response.send_message(embed=emb)

    @app_commands.command(name="user", description="User info")
    async def user(self, interaction: discord.Interaction, user: discord.User=None):
        u = user or interaction.user
        emb = discord.Embed(title=str(u), description=f"ID: {u.id}", color=discord.Color.dark_embed())
        await interaction.response.send_message(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))

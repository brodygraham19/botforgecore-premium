from __future__ import annotations
import discord
from discord import app_commands
from discord.ext import commands
from .helpers import parse_color

MIDNIGHT = 0x0f172a

class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    embed = app_commands.Group(name="embed", description="Create and send midnight-blue embeds")

    @embed.command(name="create", description="Preview an embed (ephemeral)")
    @app_commands.describe(
        title="Embed title",
        description="Main description (supports line breaks)",
        color_hex="Hex color like #0f172a (optional)",
        image_url="Image URL (optional)",
        thumbnail_url="Thumbnail URL (optional)",
        footer="Footer text (optional)"
    )
    async def create(self, interaction: discord.Interaction,
                     title: str,
                     description: str,
                     color_hex: str = None,
                     image_url: str = None,
                     thumbnail_url: str = None,
                     footer: str = None):
        colour = parse_color(color_hex, MIDNIGHT)
        emb = discord.Embed(title=title, description=description, color=colour)
        if image_url:
            emb.set_image(url=image_url)
        if thumbnail_url:
            emb.set_thumbnail(url=thumbnail_url)
        if footer:
            emb.set_footer(text=footer)
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @embed.command(name="send", description="Send a built embed to a channel")
    @app_commands.describe(
        channel="Where to post the embed",
        title="Embed title",
        description="Main description",
        color_hex="Hex color like #0f172a (optional)",
        image_url="Image URL (optional)",
        thumbnail_url="Thumbnail URL (optional)",
        footer="Footer text (optional)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, interaction: discord.Interaction,
                   channel: discord.TextChannel,
                   title: str,
                   description: str,
                   color_hex: str = None,
                   image_url: str = None,
                   thumbnail_url: str = None,
                   footer: str = None):
        colour = parse_color(color_hex, MIDNIGHT)
        emb = discord.Embed(title=title, description=description, color=colour)
        if image_url:
            emb.set_image(url=image_url)
        if thumbnail_url:
            emb.set_thumbnail(url=thumbnail_url)
        if footer:
            emb.set_footer(text=footer)
        await channel.send(embed=emb)
        await interaction.response.send_message(f"✅ Embed sent to {channel.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))

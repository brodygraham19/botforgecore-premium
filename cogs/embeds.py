from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from .helpers import parse_color

MIDNIGHT = 0x0f172a

class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    group = app_commands.Group(name="embed", description="Create and send custom embeds")

    @group.command(name="send", description="Send an embed to a channel")
    @app_commands.describe(channel="Target channel", title="Embed title", description="Embed description",
                           color_hex="Hex color like #0f172a (optional)", image_url="Image URL (optional)",
                           thumbnail_url="Thumbnail URL (optional)", footer="Footer (optional)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str,
                   color_hex: str | None=None, image_url: str | None=None, thumbnail_url: str | None=None, footer: str | None=None):
        colour = parse_color(color_hex, MIDNIGHT)
        e = discord.Embed(title=title, description=description, colour=colour)
        if image_url: e.set_image(url=image_url)
        if thumbnail_url: e.set_thumbnail(url=thumbnail_url)
        if footer: e.set_footer(text=footer)
        await channel.send(embed=e)
        await interaction.response.send_message(f"✅ Sent to {channel.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))

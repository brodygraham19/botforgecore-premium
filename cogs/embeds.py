import discord
from discord import app_commands
from discord.ext import commands

MIDNIGHT_BLUE = 0x0E1A2B
ACCENT_GREEN = 0x33FFB3
ACCENT_RED = 0xFF4D4D
ACCENT_GOLD = 0xFFB84D

def color_from_choice(name: str) -> int:
    return {
        "midnight": MIDNIGHT_BLUE,
        "green": ACCENT_GREEN,
        "red": ACCENT_RED,
        "gold": ACCENT_GOLD,
        "none": discord.Colour.default().value,
    }.get(name, MIDNIGHT_BLUE)

class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(name="embed", description="Create and send custom embeds")

    @group.command(name="send", description="Send a custom embed to this channel (or a selected channel).")
    @app_commands.describe(
        title="Embed title",
        description="Main text of the embed",
        color="Brand color",
        image_url="Optional image URL",
        footer="Optional footer text",
        channel="Target channel (defaults to current)",
        ping_role="Role to mention (optional)"
    )
    @app_commands.choices(color=[
        app_commands.Choice(name="Midnight Blue (brand)", value="midnight"),
        app_commands.Choice(name="Green", value="green"),
        app_commands.Choice(name="Red", value="red"),
        app_commands.Choice(name="Gold", value="gold"),
        app_commands.Choice(name="None (default)", value="none"),
    ])
    async def send(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: app_commands.Choice[str],
        image_url: str | None = None,
        footer: str | None = None,
        channel: discord.TextChannel | None = None,
        ping_role: discord.Role | None = None,
    ):
        embed = discord.Embed(title=title, description=description, colour=color_from_choice(color.value))
        if image_url:
            embed.set_image(url=image_url)
        if footer:
            embed.set_footer(text=footer)
        if not channel:
            channel = interaction.channel  # type: ignore
        content = ping_role.mention if ping_role else None
        await channel.send(content=content, embed=embed, allowed_mentions=discord.AllowedMentions(roles=True, users=False, everyone=False))
        await interaction.response.send_message("✅ Embed sent.", ephemeral=True)

    @group.command(name="template", description="Send a quick template embed.")
    @app_commands.describe(kind="Pick a template", message="Optional extra text")
    @app_commands.choices(kind=[
        app_commands.Choice(name="Success", value="success"),
        app_commands.Choice(name="Warning", value="warn"),
        app_commands.Choice(name="Error", value="error"),
        app_commands.Choice(name="Info", value="info"),
    ])
    async def template(self, interaction: discord.Interaction, kind: app_commands.Choice[str], message: str | None = None):
        mapping = {
            "success": ("Success", ACCENT_GREEN),
            "warn": ("Heads up", ACCENT_GOLD),
            "error": ("Error", ACCENT_RED),
            "info": ("Info", MIDNIGHT_BLUE),
        }
        title, colour = mapping[kind.value]
        embed = discord.Embed(title=title, description=message or "—", colour=colour)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))

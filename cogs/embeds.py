
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

MIDNIGHT = 0x0a192f  # midnight-blue
ACCENT = 0x0f3460     # accent blue

COLOR_CHOICES = [
    app_commands.Choice(name="Midnight Blue", value=str(MIDNIGHT)),
    app_commands.Choice(name="Accent Blue", value=str(ACCENT)),
    app_commands.Choice(name="Red", value=str(0xE11D48)),
    app_commands.Choice(name="Green", value=str(0x22C55E)),
    app_commands.Choice(name="Yellow", value=str(0xF59E0B)),
    app_commands.Choice(name="Purple", value=str(0x8B5CF6)),
    app_commands.Choice(name="Black", value=str(0x000000)),
    app_commands.Choice(name="White", value=str(0xFFFFFF)),
]

class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show ForgeBot help menu")
    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(
            title="ForgeBot — Commands",
            description=(
                "**Admin:** `/post_verify`, `/post_ticket`, `/purge`\n"
                "**Moderation:** `/ban`, `/kick`, `/mute`, `/timeout`, `/warn`\n"
                "**Utility:** `/avatar`, `/user`, `/server`, `/roleinfo`, `/ping`\n"
                "**Fun:** `/roll`, `/choose`, `/8ball`\n"
                "**Embeds:** `/embed_send`, `/embed_template`"
            ),
            color=0x0a192f
        )
        e.set_footer(text="Midnight-blue theme • Safe for public servers")
        await interaction.response.send_message(embed=e, ephemeral=True)

    @app_commands.command(name="embed_send", description="Send a custom embed to the current channel.")
    @app_commands.describe(
        title="Embed title",
        description="Main text / description",
        color="Pick a color",
        thumbnail="Thumbnail image URL (optional)",
        image="Main image URL (optional)",
        footer="Footer text (optional)",
        mention_everyone="Mention @everyone? (Default: No)"
    )
    @app_commands.choices(color=COLOR_CHOICES)
    async def embed_send(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: Optional[app_commands.Choice[str]] = None,
        thumbnail: Optional[str] = None,
        image: Optional[str] = None,
        footer: Optional[str] = None,
        mention_everyone: Optional[bool] = False
    ):
        cval = int(color.value) if color else 0x0a192f
        embed = discord.Embed(title=title, description=description, color=cval)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)
        if footer:
            embed.set_footer(text=footer)

        content = "@everyone" if mention_everyone else None
        await interaction.response.send_message(
            content=content,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(everyone=bool(mention_everyone))
        )

    @app_commands.command(name="embed_template", description="Send a pre-styled ForgeBot embed template.")
    async def embed_template(self, interaction: discord.Interaction):
        e = discord.Embed(
            title="ForgeBot Announcement",
            description="Your message here.\n\n• Point A\n• Point B\n• Point C",
            color=0x0a192f
        )
        e.set_thumbnail(url="https://i.imgur.com/KLPk7T5.png")  # generic icon
        e.set_footer(text="ForgeBot • Midnight Blue")
        await interaction.response.send_message(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(Embeds(bot))

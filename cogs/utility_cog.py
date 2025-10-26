from __future__ import annotations
import discord, json, asyncio
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Create a quick poll with reactions")
    async def poll(self, interaction: discord.Interaction, question: str, option1: str="👍", option2: str="👎"):
        await interaction.response.defer()
        embed = discord.Embed(title="📊 Poll", description=question, color=COLOR)
        msg = await interaction.channel.send(embed=embed)
        try:
            await msg.add_reaction(option1)
            await msg.add_reaction(option2)
        except discord.HTTPException:
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        await interaction.followup.send("Poll created.", ephemeral=True)

    @app_commands.command(description="Set channel slowmode (seconds)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"Slowmode set to {seconds}s.", ephemeral=True)

    @app_commands.command(description="Clear the last N messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 10):
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

    @app_commands.command(description="Show information about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        e = discord.Embed(title=f"{member}", color=COLOR)
        e.add_field(name="ID", value=member.id)
        e.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style='R') if member.joined_at else "—")
        e.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style='R'))
        e.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=e)

    @app_commands.command(description="Show server information")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        e = discord.Embed(title=g.name, color=COLOR)
        e.add_field(name="Members", value=g.member_count)
        e.add_field(name="Boosts", value=g.premium_subscription_count)
        e.add_field(name="Created", value=discord.utils.format_dt(g.created_at, style='R'))
        if g.icon:
            e.set_thumbnail(url=g.icon.url)
        await interaction.response.send_message(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))

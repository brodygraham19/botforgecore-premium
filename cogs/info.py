import discord
from discord import app_commands
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Show info about a user.")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user  # type: ignore
        embed = discord.Embed(title=f"User Info: {member}", colour=0x0E1A2B)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at, style="R") if member.joined_at else "—")
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at, style="R"))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Show info about this server.")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"{g.name}", description=f"ID: {g.id}", colour=0x0E1A2B)
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Members", value=g.member_count)
        embed.add_field(name="Owner", value=f"{g.owner}" if g.owner else "—")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))

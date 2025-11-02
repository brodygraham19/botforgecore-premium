
import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! `{round(self.bot.latency*1000)}ms`")

    @app_commands.command(name="say", description="Make the bot say a message")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅ Sent.", ephemeral=True)
        await interaction.channel.send(message)

    @app_commands.command(name="announce", description="Send an announcement embed")
    async def announce(self, interaction: discord.Interaction, title: str, message: str):
        embed = discord.Embed(title=title, description=message, color=0x2b2d31)
        await interaction.response.send_message("📢 Announcement sent.", ephemeral=True)
        await interaction.channel.send(embed=embed)

    @app_commands.command(name="help", description="Show command categories")
    async def helpcmd(self, interaction: discord.Interaction):
        embed = discord.Embed(title="ForgeBot — Commands", color=0x2b2d31, description=(
            "**Moderation**: /ban /kick /mute /unmute /clear /warn /warnings\n"
            "**Tickets**: /ticket_panel /ticket_close /ticket_add /ticket_remove\n"
            "**Verify**: /verifypanel /verify\n"
            "**Utilities**: /ping /say /announce /serverinfo /userinfo\n"
            "**Roles**: /rolebutton\n"
            "**Giveaways**: /gstart\n"
        ))
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="serverinfo", description="Show server info")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=g.name, color=0x2b2d31)
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Boosts", value=str(g.premium_subscription_count))
        if g.owner:
            embed.add_field(name="Owner", value=g.owner.mention, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="userinfo", description="Show user info")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(title=str(user), color=user.top_role.color if user.top_role else 0x2b2d31)
        if user.joined_at:
            embed.add_field(name="Joined", value=discord.utils.format_dt(user.joined_at, style='R'))
        embed.add_field(name="Account", value=discord.utils.format_dt(user.created_at, style='R'))
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))

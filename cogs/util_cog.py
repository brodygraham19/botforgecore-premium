
# cogs/util_cog.py
import platform, time, datetime
import discord
from discord import app_commands
from discord.ext import commands

BRAND_COLOR = discord.Color(0x0B1220)

class UtilCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_ts = time.time()

    @app_commands.command(name="ping", description="Latency check.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓 Pong! {round(self.bot.latency*1000)}ms", ephemeral=True)

    @app_commands.command(name="about", description="About the bot.")
    async def about(self, interaction: discord.Interaction):
        up = int(time.time() - self.start_ts)
        embed = discord.Embed(title="ForgeBot • Premium (Safe)", color=BRAND_COLOR,
                              description="All-in-one public-safe management bot.\nMidnight-blue theme.")
        embed.add_field(name="Uptime", value=f"{up//3600}h {(up%3600)//60}m", inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="invite", description="Get the bot invite link.")
    async def invite(self, interaction: discord.Interaction):
        app = await self.bot.application_info()
        url = discord.utils.oauth_url(app.id, permissions=discord.Permissions(
            send_messages=True, embed_links=True, manage_channels=True, manage_roles=True, read_message_history=True
        ), scopes=("bot", "applications.commands"))
        await interaction.response.send_message(f"🔗 Invite: {url}", ephemeral=True)

    @app_commands.command(name="help", description="Show all commands.")
    async def help(self, interaction: discord.Interaction):
        lines = [
            "**General**: /ping, /about, /invite, /help",
            "**Embeds**: /embed preview, send, template_*",
            "**Moderation**: /clear, /timeout, /kick, /ban, /warn, /warnings",
            "**Verify**: /verify_panel",
            "**Tickets**: /ticket_panel",
            "**Utility**: /avatar, /userinfo, /serverinfo, /roleinfo, /say",
            "**Fun**: /8ball, /coinflip, /roll",
            "**Admin**: /announce, /slowmode, /lock, /unlock",
        ]
        embed = discord.Embed(title="ForgeBot Commands", description="\n".join(lines), color=BRAND_COLOR)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="avatar", description="Show a user's avatar.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User | None = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"{user.name}'s Avatar", color=BRAND_COLOR)
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Info about a user.")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member | None = None):
        user = user or interaction.user
        embed = discord.Embed(title=f"User Info — {user}", color=BRAND_COLOR)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Joined", value=getattr(user, "joined_at", "Unknown"))
        embed.add_field(name="Top Role", value=getattr(user, "top_role", "N/A"))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Info about this server.")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        if not g:
            await interaction.response.send_message("Use this in a server.", ephemeral=True); return
        embed = discord.Embed(title=f"{g.name}", description="Server information", color=BRAND_COLOR)
        embed.add_field(name="Members", value=g.member_count)
        embed.add_field(name="Channels", value=len(g.channels))
        embed.set_thumbnail(url=g.icon.url if g.icon else discord.Embed.Empty)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roleinfo", description="Info about a role.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        embed = discord.Embed(title=f"Role Info — {role.name}", color=BRAND_COLOR)
        embed.add_field(name="ID", value=role.id)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Color", value=str(role.color))
        await interaction.response.send_message(embed=embed)

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name="say", description="Make the bot say something (staff only).")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅ Sent.", ephemeral=True)
        await interaction.channel.send(message)

async def setup(bot: commands.Bot):
    await bot.add_cog(UtilCog(bot))

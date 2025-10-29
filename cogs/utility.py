import platform, time, discord
from discord import app_commands
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(description="Show latency and uptime.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        uptime = round(time.time() - self.start_time)
        hrs, rem = divmod(uptime, 3600)
        mins, secs = divmod(rem, 60)
        embed = discord.Embed(title="ForgeBot Status", colour=0x0E1A2B)
        embed.add_field(name="Latency", value=f"{latency} ms")
        embed.add_field(name="Uptime", value=f"{hrs}h {mins}m {secs}s")
        embed.set_footer(text=f"discord.py {discord.__version__}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(description="Say something via the bot (no @everyone/@here).")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message("✅ Sent.", ephemeral=True)
        await interaction.channel.send(message, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True))  # type: ignore

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))

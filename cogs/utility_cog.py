from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
class UtilityCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="Quick poll")
    async def poll(self, interaction: discord.Interaction, question: str, yes: str="👍", no: str="👎"):
        e = discord.Embed(title="📊 Poll", description=question, color=COLOR)
        m = await interaction.channel.send(embed=e); await m.add_reaction(yes); await m.add_reaction(no)
        await interaction.response.send_message("Poll posted.", ephemeral=True)
async def setup(bot): await bot.add_cog(UtilityCog(bot))

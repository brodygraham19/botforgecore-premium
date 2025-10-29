import random, discord
from discord import app_commands
from discord.ext import commands
RESPONSES = ["Yes.", "No.", "Maybe...", "Ask again later.", "Absolutely!", "Not a chance."]

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Ask the 8ball a question.")
    async def eightball(self, interaction: discord.Interaction, question: str):
        await interaction.response.send_message(f"🎱 **{random.choice(RESPONSES)}**", ephemeral=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))


# cogs/fun_cog.py
import random
import discord
from discord import app_commands
from discord.ext import commands

BRAND_COLOR = discord.Color(0x0B1220)

class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball.")
    async def eightball(self, interaction: discord.Interaction, question: str):
        answers = ["It is certain.", "Most likely.", "Ask again later.", "Don't count on it.", "Very doubtful.", "Yes.", "No."]
        await interaction.response.send_message(embed=discord.Embed(
            title="🎱 Magic 8-Ball",
            description=f"**Q:** {question}\n**A:** {random.choice(answers)}",
            color=BRAND_COLOR))

    @app_commands.command(name="coinflip", description="Flip a coin.")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🪙 {random.choice(['Heads', 'Tails'])}!")

    @app_commands.command(name="roll", description="Roll NdM dice (e.g., 2d6).")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        try:
            n, m = map(int, dice.lower().split("d"))
            n = max(1, min(20, n)); m = max(2, min(1000, m))
        except Exception:
            await interaction.response.send_message("Use format NdM, e.g., 2d6.", ephemeral=True); return
        rolls = [random.randint(1, m) for _ in range(n)]
        await interaction.response.send_message(f"🎲 {dice}: **{sum(rolls)}** ({', '.join(map(str, rolls))})")

async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))

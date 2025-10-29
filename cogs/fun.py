
import random
import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Roll a dice. Example: 1d20")
    async def roll(self, interaction: discord.Interaction, dice: str="1d6"):
        try:
            n, sides = dice.lower().split("d")
            n, sides = int(n), int(sides)
            rolls = [random.randint(1, sides) for _ in range(n)]
            await interaction.response.send_message(f"🎲 {dice}: {rolls} = **{sum(rolls)}**")
        except Exception:
            await interaction.response.send_message("Use format like `1d20`.", ephemeral=True)

    @app_commands.command(name="choose", description="Let the bot choose. Separate choices with |")
    async def choose(self, interaction: discord.Interaction, options: str):
        parts = [p.strip() for p in options.split("|") if p.strip()]
        if not parts:
            await interaction.response.send_message("Give me choices separated by `|`", ephemeral=True)
            return
        await interaction.response.send_message(f"I pick: **{random.choice(parts)}**")

    @app_commands.command(name="8ball", description="Ask the magic 8-ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        answers = [
            "It is certain.", "Without a doubt.", "Yes.", "Ask again later.",
            "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
            "My reply is no.", "Very doubtful."
        ]
        await interaction.response.send_message(f"🎱 {random.choice(answers)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))

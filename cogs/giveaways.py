from __future__ import annotations
import random, asyncio
import discord
from discord.ext import commands
from discord import app_commands

MIDNIGHT = 0x0f172a

class JoinView(discord.ui.View):
    def __init__(self, duration: int, winners: int):
        super().__init__(timeout=duration)
        self.entrants: set[int] = set()
        self.winners_count = winners

    @discord.ui.button(label="🎉 Join", style=discord.ButtonStyle.primary, custom_id="forge:join_giveaway")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.entrants.add(interaction.user.id)
        await interaction.response.send_message("You're in! 🎟", ephemeral=True)

class Giveaways(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="giveaway", description="Start a button-based giveaway")
    @app_commands.describe(duration_minutes="How long to run (minutes)", winners="Number of winners", prize="What are you giving away?")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway(self, interaction: discord.Interaction, duration_minutes: int, winners: int, prize: str):
        view = JoinView(duration_minutes*60, winners)
        emb = discord.Embed(title="🎉 Giveaway", description=f"Prize: **{prize}**
Click Join to enter. Ends in ~{duration_minutes} minutes.", color=discord.Color(MIDNIGHT))
        await interaction.response.send_message(embed=emb, view=view)
        await asyncio.sleep(duration_minutes*60)
        entrants = list(view.entrants)
        if not entrants:
            await interaction.followup.send("No entries, giveaway cancelled.")
            return
        random.shuffle(entrants)
        chosen = entrants[:max(1, winners)]
        mentions = " ".join(f"<@{i}>" for i in chosen)
        await interaction.followup.send(f"🎉 Winners for **{prize}**: {mentions} — congrats!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaways(bot))

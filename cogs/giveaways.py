
import discord, asyncio, re
from discord.ext import commands
from discord import app_commands

def parse_duration(text: str) -> int:
    """Return seconds from strings like 10m, 2h, 1d."""
    m = re.match(r"^(\d+)([smhd])$", text.lower())
    if not m: return 0
    n, unit = int(m.group(1)), m.group(2)
    return n * {"s":1,"m":60,"h":3600,"d":86400}[unit]

class Giveaways(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @app_commands.command(name="gstart", description="Start a giveaway: duration like 10m, prize text")
    async def gstart(self, interaction: discord.Interaction, duration: str, prize: str):
        secs = parse_duration(duration)
        if secs <= 0: return await interaction.response.send_message("Use durations like `10m`, `2h`, `1d`.", ephemeral=True)
        embed = discord.Embed(title="🎉 Giveaway!", description=f"**Prize:** {prize}\nReact with 🎉 to enter!\nEnds in **{duration}**", color=0x9b59b6)
        msg = await interaction.channel.send(embed=embed)
        await msg.add_reaction("🎉")
        await interaction.response.send_message("✅ Giveaway started.", ephemeral=True)
        await asyncio.sleep(secs)
        # fetch again to get reactions
        msg = await interaction.channel.fetch_message(msg.id)
        users = set()
        for r in msg.reactions:
            if str(r.emoji) == "🎉":
                async for u in r.users():
                    if not u.bot:
                        users.add(u)
        if not users:
            return await interaction.channel.send("No valid entrants. 😔")
        import random
        winner = random.choice(list(users))
        await interaction.channel.send(f"🎉 **Winner:** {winner.mention} — Prize: **{prize}**")

async def setup(bot):
    await bot.add_cog(Giveaways(bot))

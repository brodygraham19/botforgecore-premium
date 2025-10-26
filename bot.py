import os
import json
import logging
import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv

# ----------------- Setup -----------------
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Missing DISCORD_BOT_TOKEN in environment.")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s"
)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = False

# Config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#", ""), 16)

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
            activity=discord.Game(name="Forging your bots 🔥")
        )
        self.synced = False

    async def setup_hook(self):
        # Load extensions
        for ext in (
            "cogs.setup_cog",
            "cogs.verify_cog",
            "cogs.ticket_cog",
            "cogs.shop_cog",
            "cogs.branding_cog",
            "cogs.utility_cog",
            "cogs.moderation_cog",
            "cogs.announce_cog",
        ):
            await self.load_extension(ext)

    async def on_ready(self):
        if not self.synced:
            await self.tree.sync()
            self.synced = True
            logging.info("Slash commands synced.")
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")

bot = ForgeBot()

# Simple /ping, /uptime, /status here for convenience
start_time = datetime.now(timezone.utc)

@bot.tree.command(description="Check if ForgeBot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)} ms")

@bot.tree.command(description="Show how long the bot has been running")
async def uptime(interaction: discord.Interaction):
    delta = datetime.now(timezone.utc) - start_time
    hrs, rem = divmod(int(delta.total_seconds()), 3600)
    mins, secs = divmod(rem, 60)
    await interaction.response.send_message(f"Uptime: {hrs}h {mins}m {secs}s")

@bot.tree.command(description="Basic status info")
async def status(interaction: discord.Interaction):
    guilds = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds)
    embed = discord.Embed(title="ForgeBot Status", color=COLOR)
    embed.add_field(name="Guilds", value=str(guilds))
    embed.add_field(name="Users", value=str(users))
    embed.add_field(name="Latency", value=f"{round(bot.latency*1000)} ms")
    await interaction.response.send_message(embed=embed)

# Run
if __name__ == "__main__":
    bot.run(TOKEN)

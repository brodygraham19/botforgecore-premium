
# ForgeBot – Premium (No Stocks)
# --------------------------------
# Includes:
#   - /embed commands (preview, send, templates)
#   - Moderation: /purge, /timeout, /kick, /ban
#   - Utility: /ping, /serverinfo, /avatar, /say
#   - Verification via button & role assignment
#   - Tickets via button, per-user private channel, close button
#
# Quick Start:
#   pip install -r requirements.txt
#   copy .env.example .env  (fill values)
#   python bot.py

import os
import logging
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # optional for fast command sync
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")  # used by verify_cog
STAFF_ROLE_ID = os.getenv("STAFF_ROLE_ID")    # used by ticket_cog
TICKETS_CATEGORY_ID = os.getenv("TICKETS_CATEGORY_ID")  # used by ticket_cog

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("forgebot")

intents = discord.Intents.default()
intents.members = True  # needed for role assignment in verify
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "cogs.embed_cog",
    "cogs.util_cog",
    "cogs.moderation_cog",
    "cogs.verify_cog",
    "cogs.ticket_cog",
]

async def load_extensions():
    for ext in COGS:
        try:
            await bot.load_extension(ext)
            log.info("Loaded %s", ext)
        except Exception as e:
            log.exception("Failed to load %s: %s", ext, e)

@bot.event
async def on_ready():
    await load_extensions()
    # Sync slash commands
    try:
        if GUILD_ID:
            gid = int(GUILD_ID)
            await bot.tree.sync(guild=discord.Object(id=gid))
            log.info("Slash commands synced to guild %s", gid)
        else:
            await bot.tree.sync()
            log.info("Slash commands synced globally")
    except Exception as e:
        log.exception("Slash sync failed: %s", e)

    log.info("Logged in as %s (%s)", bot.user, bot.user.id)

# Global app command error handler for friendly messages
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: Exception):
    try:
        await interaction.response.send_message(f"❌ {error}", ephemeral=True)
    except discord.InteractionResponded:
        await interaction.followup.send(f"❌ {error}", ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in .env")
    bot.run(TOKEN)

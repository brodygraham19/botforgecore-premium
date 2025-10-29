
import os
import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

# ------------------------------
# Logging
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("forgebot")

# ------------------------------
# Env & Intents
# ------------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # optional: speed up sync for one guild
OWNER_ID = int(os.getenv("OWNER_ID", "0")) or None

intents = discord.Intents.default()
intents.message_content = False  # safer for public servers
intents.members = True
intents.guilds = True
intents.reactions = True

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),  # legacy prefix for owners
            intents=intents,
            help_command=None,
            owner_id=OWNER_ID
        )
        self.synced = False

    async def setup_hook(self) -> None:
        # Load cogs automatically
        for cog in (
            "cogs.embeds",
            "cogs.utility",
            "cogs.fun",
            "cogs.moderation",
            "cogs.admin",
            "cogs.tickets",
            "cogs.verify",
        ):
            try:
                await self.load_extension(cog)
                logger.info("Loaded %s", cog)
            except Exception as e:
                logger.exception("Failed to load %s: %s", cog, e)

        # Sync app commands
        try:
            if GUILD_ID:
                guild = discord.Object(id=int(GUILD_ID))
                await self.tree.sync(guild=guild)
                logger.info("Slash commands synced to guild %s", GUILD_ID)
            else:
                await self.tree.sync()
                logger.info("Slash commands globally synced")
        except Exception:
            logger.exception("Failed to sync application commands")

    async def on_ready(self):
        logger.info("Logged in as %s (%s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Game(name="ForgeBot • /help"),
            status=discord.Status.online
        )

bot = ForgeBot()

# ---------------
# Safe error handler
# ---------------
@bot.tree.error
async def on_app_error(interaction: discord.Interaction, error: Exception):
    logger.exception("App command error: %s", error)
    if interaction.response.is_done():
        await interaction.followup.send("❌ An error occurred.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An error occurred.", ephemeral=True)

# ---------------
# Run
# ---------------
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in environment.")
    bot.run(TOKEN)

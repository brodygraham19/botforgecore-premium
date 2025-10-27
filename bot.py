import os, json, logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Missing DISCORD_BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

with open("config.json","r") as f:
    CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents, help_command=None)
        self.synced = False

    async def setup_hook(self):
        for ext in [
            "cogs.setup_cog",
            "cogs.verify_cog",
            "cogs.ticket_cog",
            "cogs.shop_cog",
            "cogs.branding_cog",
            "cogs.utility_cog",
            "cogs.moderation_cog",
            "cogs.announce_cog",
            "cogs.verify_button_cog",
            "cogs.ticket_button_cog",
        ]:
            await self.load_extension(ext)

bot = ForgeBot()

@bot.event
async def on_ready():
    if not bot.synced:
        await bot.tree.sync()
        bot.synced = True
        logging.info("Slash commands synced.")
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

bot.run(TOKEN)

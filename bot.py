
import os, asyncio, logging
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
STATUS_ROTATOR_ENABLED = os.getenv("STATUS_ROTATOR_ENABLED", "true").lower() == "true"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    # Faster guild-scoped sync if GUILD_ID provided
    if GUILD_ID and GUILD_ID.isdigit():
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        logging.info(f"✅ Slash commands synced to guild {GUILD_ID}")
    else:
        await bot.tree.sync()
        logging.info("✅ Global slash commands synced")

    # register persistent button views from cogs
    for cog in bot.cogs.values():
        setup_persistent = getattr(cog, "setup_persistent_views", None)
        if callable(setup_persistent):
            await setup_persistent()

    if STATUS_ROTATOR_ENABLED and not status_rotator.is_running():
        status_rotator.start()

@tasks.loop(seconds=20)
async def status_rotator():
    statuses = [
        "Project Hyper 2.0",
        "Type /help",
        "Moderating your server",
        "Tickets & Verifications",
    ]
    for s in statuses:
        await bot.change_presence(activity=discord.Game(name=s))
        await asyncio.sleep(15)

async def load_extensions():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                logging.info(f"Loaded cog: {file}")
            except Exception as e:
                logging.exception(f"Failed to load {file}: {e}")

async def main():
    if not TOKEN:
        raise SystemExit("Missing DISCORD_TOKEN in environment.")
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

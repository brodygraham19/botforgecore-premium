
import os, asyncio, logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    logging.info(f"✅ Logged in as {bot.user}")
    if GUILD_ID and GUILD_ID.isdigit():
        guild = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    else:
        await bot.tree.sync()
    for cog in bot.cogs.values():
        if hasattr(cog, "setup_persistent_views"):
            await cog.setup_persistent_views()

async def load_extensions():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

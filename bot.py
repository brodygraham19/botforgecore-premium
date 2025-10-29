#!/usr/bin/env python3
import os, logging, asyncio, discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")
GUILD_ID = os.getenv("GUILD_ID")
OWNER_IDS = {int(x) for x in os.getenv("OWNER_IDS", "").split(",") if x.strip().isdigit()}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s: %(message)s")
log = logging.getLogger("forgebot")

intents = discord.Intents(guilds=True, messages=True, message_content=False, members=True, bans=True, emojis=True, voice_states=True, reactions=True)

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents, application_id=int(APPLICATION_ID) if APPLICATION_ID else None, help_command=None)

    async def setup_hook(self):
        for fname in os.listdir("cogs"):
            if fname.endswith(".py") and not fname.startswith("_"):
                await self.load_extension(f"cogs.{fname[:-3]}")
                log.info("Loaded cog: %s", fname)
        try:
            if GUILD_ID:
                cmds = await self.tree.sync(guild=discord.Object(id=int(GUILD_ID)))
                log.info("Synced %d guild commands to %s", len(cmds), GUILD_ID)
            else:
                cmds = await self.tree.sync()
                log.info("Globally synced %d commands", len(cmds))
        except Exception as e:
            log.exception("Slash sync failed: %s", e)

    async def on_ready(self):
        log.info("Logged in as %s (%s)", self.user, self.user.id)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Forge"))

bot = ForgeBot()

@bot.command(name="reload")
@commands.is_owner()
async def reload_cog(ctx: commands.Context, cog: str):
    try:
        await bot.reload_extension(f"cogs.{cog}")
    except Exception as e:
        await ctx.reply(f"Reload failed: `{e}`")
    else:
        await ctx.reply("Reloaded ✅")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    log.exception("Slash command error: %s", error)
    if interaction.response.is_done():
        await interaction.followup.send("⚠️ Something went wrong while running that command.", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Something went wrong while running that command.", ephemeral=True)

def main():
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in environment.")
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

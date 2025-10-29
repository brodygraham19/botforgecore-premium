from __future__ import annotations
import os, logging, discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID","0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("ForgeBot")

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="FORGEBOT_SLASH_ONLY",
            intents=intents,
            help_command=None,
            activity=discord.Activity(type=discord.ActivityType.watching, name="Forge • /help"),
        )

    async def setup_hook(self):
        # Load cogs
        for ext in ("cogs.welcome","cogs.embeds","cogs.moderation","cogs.automod","cogs.tickets","cogs.utilities","cogs.giveaways"):
            try:
                await self.load_extension(ext); log.info("Loaded %s", ext)
            except Exception as e:
                log.exception("Failed to load %s: %s", ext, e)

        # Sync slash commands
        if GUILD_ID:
            g = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=g)
            await self.tree.sync(guild=g)
            log.info("Slash commands synced to guild %s", GUILD_ID)
        else:
            await self.tree.sync()
            log.info("Slash commands globally synced")

    async def on_ready(self):
        log.info("Logged in as %s (%s)", self.user, self.user.id)
        # Persist views so buttons still work after restarts
        try:
            from cogs.welcome import VerifyView
            from cogs.tickets import TicketView, CloseTicketView
            verified_role_id = int(os.getenv("VERIFIED_ROLE_ID","0"))
            unverified_role_id = int(os.getenv("UNVERIFIED_ROLE_ID","0"))
            self.add_view(VerifyView(verified_role_id, unverified_role_id))
            self.add_view(TicketView()); self.add_view(CloseTicketView())
        except Exception as e:
            log.warning("Persistent view registration failed: %s", e)

bot = ForgeBot()

@bot.tree.command(name="help", description="Show ForgeBot commands")
async def help_cmd(interaction: discord.Interaction):
    txt = (
        "**ForgeBot** (midnight-blue)\n"
        "• `/rules_panel` — rules + Verify button\n"
        "• `/ticket_panel` — ticket open button\n"
        "• `/embed send` — custom embeds\n"
        "• `/clear` `/timeout` `/kick` `/ban` — moderation\n"
        "• `/ping` `/avatar` `/userinfo` `/serverinfo` — utilities\n"
        "• `/giveaway` — start a giveaway\n"
    )
    await interaction.response.send_message(txt, ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN.")
    bot.run(TOKEN)

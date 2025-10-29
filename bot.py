from __future__ import annotations
import os, asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID","0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            activity=discord.Game(name="/help | ForgeBot"),
        )

    async def setup_hook(self):
        # load cogs
        for ext in ("cogs.welcome","cogs.embeds","cogs.moderation","cogs.automod","cogs.tickets","cogs.utilities","cogs.giveaways"):
            await self.load_extension(ext)

        # sync commands
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Synced to guild {GUILD_ID}")
        else:
            await self.tree.sync()
            print("Synced global commands")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

bot = ForgeBot()

# Basic /help listing
@bot.tree.command(name="help", description="Show ForgeBot commands")
async def help_cmd(interaction: discord.Interaction):
    text = (
        "**ForgeBot** (midnight-blue)
"
        "• `/rules_panel` – post rules + Verify button
"
        "• `/ticket_panel` – post ticket button
"
        "• `/embed create|send` – build embeds
"
        "• `/purge` `/kick` `/ban` `/timeout` – moderation
"
        "• `/ping` `/avatar` `/user` `/server` – utilities
"
        "• `/giveaway` – quick giveaway
"
    )
    await interaction.response.send_message(text, ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Missing DISCORD_BOT_TOKEN in environment.")
    bot.run(TOKEN)

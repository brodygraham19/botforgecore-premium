import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

class ForgeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        from cogs.verify import VerifyCog
        from cogs.ticket import TicketCog
        await self.add_cog(VerifyCog(self))
        await self.add_cog(TicketCog(self))
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        print(f"✅ Logged in as {self.user} ({self.user.id})")
        await self.change_presence(activity=discord.Game(name="ForgeBot Premium"))

bot = ForgeBot()
bot.run(TOKEN)


import discord
from discord.ext import commands

class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        from .admin import ButtonViews
        self.bot.add_view(ButtonViews.VerifyView(verified_role_id=0), message_id=None)

async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))

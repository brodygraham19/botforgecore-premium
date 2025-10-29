
import os
import discord
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self) -> None:
        # Re-register persistent component IDs so buttons keep working after restarts
        from .admin import ButtonViews
        self.bot.add_view(ButtonViews.TicketOpenView(staff_role_id=0), message_id=None)  # dummy for persistence id
        self.bot.add_view(ButtonViews.TicketCloseView(), message_id=None)

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))

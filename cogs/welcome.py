
import discord, os
from discord.ext import commands

WELCOME_CHANNEL_ID = os.getenv("WELCOME_CHANNEL_ID")
WELCOME_DM_ENABLED = os.getenv("WELCOME_DM_ENABLED", "true").lower() == "true"

class Welcome(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if WELCOME_CHANNEL_ID and WELCOME_CHANNEL_ID.isdigit():
            ch = member.guild.get_channel(int(WELCOME_CHANNEL_ID))
            if ch:
                try: await ch.send(f"👋 Welcome {member.mention}! Read rules and verify to access the server.")
                except Exception: pass
        if WELCOME_DM_ENABLED:
            try: await member.send(f"Welcome to **{member.guild.name}**! Please verify to unlock channels.")
            except Exception: pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))

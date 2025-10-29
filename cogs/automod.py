from __future__ import annotations
import os, re
import discord
from discord.ext import commands
from datetime import timedelta

LINK_RE = re.compile(r"https?://|discord\.gg", re.I)
BAD_WORDS = {"fuck","shit","bitch","bastard","slut","whore","cunt"}  # simple demo list

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.link_filter = os.getenv("LINK_FILTER","1") == "1"
        self.profanity_filter = os.getenv("PROFANITY_FILTER","1") == "1"
        self.timeout_minutes = int(os.getenv("TIMEOUT_MINUTES","10"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        perms = message.channel.permissions_for(message.author)
        if perms.manage_messages or perms.administrator:
            return  # staff bypass

        reason = None
        if self.link_filter and LINK_RE.search(message.content):
            reason = "Link posting is disabled here."
        if self.profanity_filter and any(w in message.content.lower() for w in BAD_WORDS):
            reason = "Please avoid profanity."

        if reason:
            try:
                await message.delete()
            except Exception:
                pass
            try:
                await message.author.timeout(timedelta(minutes=self.timeout_minutes), reason=f"AutoMod: {reason}")
            except Exception:
                pass
            try:
                await message.channel.send(f"⚠️ {message.author.mention} {reason} (auto-timeout {self.timeout_minutes}m).", delete_after=6)
            except Exception:
                pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))

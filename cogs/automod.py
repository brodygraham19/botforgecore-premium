from __future__ import annotations
import os, re
from datetime import timedelta
import discord
from discord.ext import commands

LINK_RE = re.compile(r"https?://|discord\.gg", re.I)
BAD = {"fuck","shit","bitch","bastard","slut","whore","cunt"}  # simple demo list

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.link_filter = os.getenv("LINK_FILTER","1") == "1"
        self.profanity = os.getenv("PROFANITY_FILTER","1") == "1"
        self.timeout_minutes = int(os.getenv("TIMEOUT_MINUTES","10"))

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if not msg.guild or msg.author.bot: return
        perms = msg.channel.permissions_for(msg.author)
        if perms.manage_messages or perms.administrator: return  # staff bypass

        reason = None
        if self.link_filter and LINK_RE.search(msg.content): reason = "Links are not allowed here."
        if self.profanity and any(w in msg.content.lower() for w in BAD): reason = "Please avoid profanity."

        if reason:
            try: await msg.delete()
            except Exception: pass
            try: await msg.author.timeout(timedelta(minutes=self.timeout_minutes), reason=f"AutoMod: {reason}")
            except Exception: pass
            try: await msg.channel.send(f"⚠️ {msg.author.mention} {reason} (auto-timeout {self.timeout_minutes}m).", delete_after=6)
            except Exception: pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))

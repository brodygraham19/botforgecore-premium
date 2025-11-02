
import discord, os, re, time
from discord.ext import commands

ANTI_INVITE = os.getenv("ANTI_INVITE_ENABLED", "true").lower() == "true"
ANTI_SPAM = os.getenv("ANTI_SPAM_ENABLED", "true").lower() == "true"
INVITE_RE = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.I)

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_times = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot: return

        # Block invite links
        if ANTI_INVITE and INVITE_RE.search(message.content):
            try:
                await message.delete()
            except Exception:
                pass

        # Basic spam bucket
        if not ANTI_SPAM: return
        now = time.time()
        window, limit = 6, 6
        bucket = self.msg_times.setdefault(message.author.id, [])
        bucket.append(now)
        self.msg_times[message.author.id] = [t for t in bucket if now - t <= window]
        if len(self.msg_times[message.author.id]) > limit:
            try:
                until = discord.utils.utcnow() + discord.timedelta(minutes=10)
                await message.author.timeout(until, reason="Auto anti-spam")
            except Exception:
                pass

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))


import discord, os
from discord.ext import commands

LOGS_CHANNEL_ID = os.getenv("LOGS_CHANNEL_ID")

class LoggingCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        try:
            if LOGS_CHANNEL_ID and LOGS_CHANNEL_ID.isdigit():
                ch = guild.get_channel(int(LOGS_CHANNEL_ID))
                if ch: await ch.send(embed=embed)
        except Exception: pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.send_log(member.guild, discord.Embed(description=f"👋 **Join:** {member.mention}", color=0x3498db))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.send_log(member.guild, discord.Embed(description=f"🚪 **Leave:** {member}", color=0xe74c3c))

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild and not message.author.bot:
            await self.send_log(message.guild, discord.Embed(description=f"🗑 **Deleted in {message.channel.mention}:** {message.author}: {message.content}", color=0x95a5a6))

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.guild and not before.author.bot and before.content != after.content:
            em = discord.Embed(title="✏️ Message Edited", color=0xf1c40f)
            em.add_field(name="Channel", value=before.channel.mention)
            em.add_field(name="Author", value=str(before.author), inline=False)
            em.add_field(name="Before", value=before.content[:500] or " ", inline=False)
            em.add_field(name="After", value=after.content[:500] or " ", inline=False)
            await self.send_log(before.guild, em)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))

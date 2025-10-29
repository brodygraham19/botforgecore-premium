import discord
from discord import app_commands
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="(Owner) Sync slash commands now.")
    async def sync(self, interaction: discord.Interaction):
        app = (await self.bot.application_info())
        if interaction.user.id != app.owner.id and interaction.user.id not in getattr(self.bot,'owner_ids', set()):
            return await interaction.response.send_message("Owner only.", ephemeral=True)
        if guild := interaction.guild:
            cmds = await self.bot.tree.sync(guild=guild)
            await interaction.response.send_message(f"Synced {len(cmds)} commands to this guild.", ephemeral=True)
        else:
            cmds = await self.bot.tree.sync()
            await interaction.response.send_message(f"Globally synced {len(cmds)} commands.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))

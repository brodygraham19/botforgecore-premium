
import discord, os
from discord.ext import commands
from discord import app_commands

VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Verify", style=discord.ButtonStyle.success, custom_id="verify_btn"))

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup_persistent_views(self):
        self.bot.add_view(VerifyView())

    @app_commands.command(name="verifypanel", description="Send verification panel")
    async def verifypanel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Verify", description="Press verify button")
        await interaction.channel.send(embed=embed, view=VerifyView())
        await interaction.response.send_message("Panel sent", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "verify_btn":
            role = interaction.guild.get_role(int(VERIFY_ROLE_ID))
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Verified!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verify(bot))

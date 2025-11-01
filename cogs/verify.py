import os
import discord
from discord.ext import commands
from discord import app_commands

VERIFY_ROLE_ID = int(os.getenv("VERIFY_ROLE_ID", "0"))

class VerifyView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="forge_verify_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            return await interaction.response.send_message("⚠️ Verify role is misconfigured.", ephemeral=True)
        try:
            await interaction.user.add_roles(role, reason="User verified")
        except discord.Forbidden:
            return await interaction.response.send_message("I don't have permission to add that role.", ephemeral=True)
        await interaction.response.send_message("✅ You are verified!", ephemeral=True)

class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Re-register persistent view on restart
        if VERIFY_ROLE_ID:
            self.bot.add_view(VerifyView(VERIFY_ROLE_ID))

    @app_commands.command(name="setup-verify", description="Post the verification button in this channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_verify(self, interaction: discord.Interaction):
        if not VERIFY_ROLE_ID:
            return await interaction.response.send_message("Set VERIFY_ROLE_ID env var first.", ephemeral=True)
        embed = discord.Embed(title="Verify to Access the Server", description="Click **Verify** to receive access.", color=0x2f3136)
        await interaction.channel.send(embed=embed, view=VerifyView(VERIFY_ROLE_ID))
        await interaction.response.send_message("✅ Posted verify panel.", ephemeral=True)

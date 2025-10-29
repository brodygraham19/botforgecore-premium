
# cogs/verify_cog.py
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
VERIFY_ROLE_ID = int(os.getenv("VERIFY_ROLE_ID") or 0)

class VerifyView(discord.ui.View):
    def __init__(self, *, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="forge_verify_btn")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild or not VERIFY_ROLE_ID:
            await interaction.response.send_message("Verification not configured.", ephemeral=True); return
        role = interaction.guild.get_role(VERIFY_ROLE_ID)
        if not role:
            await interaction.response.send_message("Verification role not found.", ephemeral=True); return
        try:
            await interaction.user.add_roles(role, reason="ForgeBot verification")
            await interaction.response.send_message("🎟️ Verified! Role added.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I need permission to manage roles (and be above the role).", ephemeral=True)

class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="verify_panel", description="Post the verify button (admins).")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verify_panel(self, interaction: discord.Interaction,
                           title: str = "Verify to Access the Server",
                           description: str = "Press the button to get verified and unlock channels."):
        embed = discord.Embed(title=title, description=description, color=discord.Color.green())
        await interaction.channel.send(embed=embed, view=VerifyView())
        await interaction.response.send_message("✅ Posted verify panel.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VerifyCog(bot))

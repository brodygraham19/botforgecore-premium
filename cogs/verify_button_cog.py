import discord
from discord.ext import commands
from discord import app_commands
import json

with open("config.json", "r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#", ""), 16)

class VerifyView(discord.ui.View):
    def __init__(self, role_name):
        super().__init__(timeout=None)
        self.role_name = role_name

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=self.role_name)
        if not role:
            return await interaction.response.send_message("Role not found.", ephemeral=True)
        if role in interaction.user.roles:
            return await interaction.response.send_message("You're already verified ✅", ephemeral=True)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("You’ve been verified!", ephemeral=True)

class VerifyButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Post a verify button panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verifypanel(self, interaction: discord.Interaction):
        e = discord.Embed(
            title="Verify to Enter",
            description="Click the button below to get verified and access the rest of the server!",
            color=COLOR
        )
        e.set_thumbnail(url=CONFIG["logo_url"])
        view = VerifyView(CONFIG["roles"]["verified"])
        await interaction.response.send_message(embed=e, view=view)

async def setup(bot):
    await bot.add_cog(VerifyButtonCog(bot))
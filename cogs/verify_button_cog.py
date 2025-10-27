import discord, json
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
class VerifyView(discord.ui.View):
    def __init__(self, role_name: str):
        super().__init__(timeout=None); self.role_name = role_name
    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success)
    async def verify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=self.role_name) or await interaction.guild.create_role(name=self.role_name, mentionable=True)
        if role in interaction.user.roles: return await interaction.response.send_message("You're already verified ✅", ephemeral=True)
        await interaction.user.add_roles(role); await interaction.response.send_message("You’re verified! Welcome 🎉", ephemeral=True)
class VerifyButtonCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="Post the Verify button panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def verifypanel(self, interaction: discord.Interaction):
        e = discord.Embed(title="Verify to Enter", description="Press **Verify** to unlock the server.", color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"]); await interaction.response.send_message(embed=e, view=VerifyView(CONFIG["roles"]["verified"]))
async def setup(bot): await bot.add_cog(VerifyButtonCog(bot))

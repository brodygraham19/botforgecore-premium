from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

class VerifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Verify yourself to get access (assigns the Verified role)")
    async def verify(self, interaction: discord.Interaction):
        guild = interaction.guild
        role_name = CONFIG["roles"]["verified"]
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, mentionable=True)
        member = interaction.user
        if role in member.roles:
            await interaction.response.send_message("You're already verified ✅", ephemeral=True)
        else:
            await member.add_roles(role, reason="Self-verified via /verify")
            await interaction.response.send_message(f"Verified! You now have {role.mention} access.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(VerifyCog(bot))

from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
import json

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

class SetupCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Auto-create BotForge roles, channels and categories")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, interaction: discord.Interaction):
        guild = interaction.guild
        await interaction.response.defer(ephemeral=True)

        # Roles
        role_names = CONFIG["roles"]
        created_roles = {}
        for key, name in role_names.items():
            role = discord.utils.get(guild.roles, name=name)
            if not role:
                role = await guild.create_role(name=name, mentionable=True)
            created_roles[key] = role

        # Channels/Categories
        cats = CONFIG["categories"]
        tickets_cat = discord.utils.get(guild.categories, name=cats["tickets"])
        if not tickets_cat:
            tickets_cat = await guild.create_category(cats["tickets"])

        ch_cfg = CONFIG["channels"]
        logs = discord.utils.get(guild.text_channels, name=ch_cfg["logs"]) or await guild.create_text_channel(ch_cfg["logs"])
        orders = discord.utils.get(guild.text_channels, name=ch_cfg["orders"]) or await guild.create_text_channel(ch_cfg["orders"])
        support = discord.utils.get(guild.text_channels, name=ch_cfg["support"]) or await guild.create_text_channel(ch_cfg["support"])
        news = discord.utils.get(guild.text_channels, name=ch_cfg["news"]) or await guild.create_text_channel(ch_cfg["news"])
        showcase = discord.utils.get(guild.text_channels, name=ch_cfg["showcase"]) or await guild.create_text_channel(ch_cfg["showcase"])

        embed = discord.Embed(title="Setup Complete ✅", color=COLOR, description="Roles, channels and ticket category created.")
        embed.add_field(name="Roles", value=", ".join([r.mention for r in created_roles.values()]))
        embed.add_field(name="Channels", value=", ".join([f"#{ch_cfg[k]}" for k in ch_cfg]))
        embed.add_field(name="Category", value=tickets_cat.name)
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))

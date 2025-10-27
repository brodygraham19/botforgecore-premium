from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

# Load config
with open("config.json","r") as f:
    CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)

# Example shop data
BOTS = [
    {"name":"Stock Bot","desc":"Price, volume spike, and news alerts.","tier":"Pro"},
    {"name":"Verify Bot","desc":"Verification panel with role system.","tier":"Basic"},
    {"name":"Ticket Bot","desc":"Support tickets with private channels.","tier":"Basic"},
    {"name":"Custom Bot","desc":"Custom built features by BotForge.","tier":"Custom"},
]

class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Show available bots in the shop")
    async def listbots(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🛠️ BotForge Shop", color=COLOR)
        for bot_item in BOTS:
            embed.add_field(
                name=f"{bot_item['name']} — {bot_item['tier']}",
                value=bot_item["desc"],
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Show pricing tiers")
    async def price(self, interaction: discord.Interaction):
        embed = discord.Embed(title="💸 Pricing Tiers", color=COLOR)
        embed.add_field(name="Basic", value="$25-$50")
        embed.add_field(name="Pro", value="$75-$150")
        embed.add_field(name="Custom", value="Ask for quote")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Open an order ticket for a custom bot")
    async def order(self, interaction: discord.Interaction, details: str="Tell us what you need"):
        g = interaction.guild
        category = discord.utils.get(g.categories, name=CONFIG["categories"]["tickets"]) or await g.create_category(CONFIG["categories"]["tickets"])
        name = f"order-{interaction.user.name}".replace(" ", "-").lower()
        overwrites = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        mod_role = discord.utils.get(g.roles, name=CONFIG["roles"]["moderator"])
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        channel = await g.create_text_channel(name, category=category, overwrites=overwrites)
        embed = discord.Embed(title="New Order", description=f"Customer: {interaction.user.mention}\nDetails: **{details}**", color=COLOR)
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Order ticket created: {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShopCog(bot))
from __future__ import annotations
import discord, json
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

BOTS = [
    {"name":"Stock Bot", "desc":"Price, volume spike, and news alerts.", "tier":"Pro"},
    {"name":"Verify Bot", "desc":"Role-based verification with buttons.", "tier":"Basic"},
    {"name":"Ticket Bot", "desc":"Private support channels with close.", "tier":"Basic"},
    {"name":"Custom Bot", "desc":"Tailored features on request.", "tier":"Custom"},
]

class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Show the list of available bots")
    async def listbots(self, interaction: discord.Interaction):
        embed = discord.Embed(title="BotForge – Available Bots", color=COLOR)
        for b in BOTS:
            embed.add_field(name=f"🧰 {b['name']} — {b['tier']}", value=b["desc"], inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Show pricing tiers")
    async def price(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Pricing", color=COLOR)
        embed.add_field(name="Basic", value="$25–$50 • Setup + simple cmds", inline=True)
        embed.add_field(name="Pro", value="$75–$150 • Data/APIs + embeds", inline=True)
        embed.add_field(name="Custom", value="Ask • Fully custom systems", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Open an order ticket")
    async def order(self, interaction: discord.Interaction, details: str = "Tell us the bot you want"):
        # Reuse ticket open
        tree = interaction.client.tree
        await interaction.response.defer(ephemeral=True)
        # open a ticket channel
        from cogs.ticket_cog import sanitize
        guild = interaction.guild
        cat_name = CONFIG["categories"]["tickets"]
        category = discord.utils.get(guild.categories, name=cat_name) or await guild.create_category(cat_name)

        chan_name = f"order-{sanitize(interaction.user.name)}"
        i = 1
        base = chan_name
        while discord.utils.get(guild.text_channels, name=chan_name):
            i += 1
            chan_name = f"{base}-{i}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        mod_role = discord.utils.get(guild.roles, name=CONFIG["roles"]["moderator"])
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        channel = await guild.create_text_channel(chan_name, overwrites=overwrites, category=category, reason="Order ticket created")
        embed = discord.Embed(title="New Order", description=f"Customer: {interaction.user.mention}\nDetails: **{details}**", color=COLOR)
        await channel.send(embed=embed)
        await interaction.followup.send(f"Order ticket created: {channel.mention}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ShopCog(bot))

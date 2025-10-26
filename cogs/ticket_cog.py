from __future__ import annotations
import discord, json, re
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#",""),16)

def sanitize(name: str) -> str:
    return re.sub(r'[^a-z0-9\-]', '-', name.lower())[:90]

class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ticket = app_commands.Group(name="ticket", description="Ticket controls")

    @ticket.command(name="open", description="Open a private support/order ticket")
    async def open_ticket(self, interaction: discord.Interaction, reason: str = "Support/Order"):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        cat_name = CONFIG["categories"]["tickets"]
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            category = await guild.create_category(cat_name)

        chan_name = f"ticket-{sanitize(interaction.user.name)}"
        # Unique channel name if exists
        i = 1
        base = chan_name
        while discord.utils.get(guild.text_channels, name=chan_name):
            i += 1
            chan_name = f"{base}-{i}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        # Allow moderators if exists
        mod_role = discord.utils.get(guild.roles, name=CONFIG["roles"]["moderator"])
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)

        channel = await guild.create_text_channel(chan_name, overwrites=overwrites, category=category, reason=f"Ticket opened: {reason}")
        embed = discord.Embed(title="New Ticket", description=f"Opened by {interaction.user.mention}\nReason: **{reason}**", color=COLOR)
        await channel.send(embed=embed)
        await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)

    @ticket.command(name="close", description="Close this ticket channel")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        channel = interaction.channel
        await interaction.response.defer(ephemeral=True)
        if isinstance(channel, discord.TextChannel) and channel.category and channel.category.name == CONFIG["categories"]["tickets"]:
            await channel.send("Closing ticket in 5 seconds…")
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
            await channel.delete(reason="Ticket closed")
        else:
            await interaction.followup.send("This command must be used inside a ticket channel.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))

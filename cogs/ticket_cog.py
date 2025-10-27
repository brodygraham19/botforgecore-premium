from __future__ import annotations
import discord, json, re
from discord.ext import commands
from discord import app_commands

with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)

def sanitize(s:str)->str:
    return re.sub(r'[^a-z0-9\-]','-',s.lower())[:90]

class TicketCog(commands.Cog):
    def __init__(self, bot): self.bot = bot

    ticket = app_commands.Group(name="ticket", description="Ticket controls")

    @ticket.command(name="open", description="Open a private ticket")
    async def open_ticket(self, interaction: discord.Interaction, reason: str="Support"):
        g = interaction.guild
        await interaction.response.defer(ephemeral=True)
        cat = discord.utils.get(g.categories, name=CONFIG["categories"]["tickets"]) or await g.create_category(CONFIG["categories"]["tickets"])
        base = f"ticket-{sanitize(interaction.user.name)}"; name = base; i=1
        while discord.utils.get(g.text_channels, name=name):
            i += 1; name = f"{base}-{i}"
        overwrites = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        mod_role = discord.utils.get(g.roles, name=CONFIG["roles"]["moderator"])
        if mod_role:
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        ch = await g.create_text_channel(name, category=cat, overwrites=overwrites)
        e = discord.Embed(title="New Ticket", description=f"Opened by {interaction.user.mention}\nReason: **{reason}**", color=COLOR)
        if mod_role: await ch.send(mod_role.mention, embed=e)
        else: await ch.send(embed=e)
        await interaction.followup.send(f"Ticket created: {ch.mention}", ephemeral=True)

    @ticket.command(name="close", description="Close this ticket")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction):
        ch = interaction.channel
        if isinstance(ch, discord.TextChannel) and ch.category and ch.category.name == CONFIG["categories"]["tickets"]:
            await interaction.response.send_message("Closing…", ephemeral=True)
            await ch.delete(reason="Ticket closed")
        else:
            await interaction.response.send_message("Use inside a ticket channel.", ephemeral=True)

async def setup(bot): await bot.add_cog(TicketCog(bot))

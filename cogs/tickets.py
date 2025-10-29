from __future__ import annotations
import os
import discord
from discord.ext import commands
from discord import app_commands
from .helpers import get_role

MIDNIGHT = 0x0f172a

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="forge:open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("Use this in a server.", ephemeral=True)

        support_role_id = int(os.getenv("SUPPORT_ROLE_ID","0"))
        support_role = get_role(guild, support_role_id, "Support Team")

        category_id = int(os.getenv("TICKET_CATEGORY_ID","0"))
        category = guild.get_channel(category_id) if category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

        name = f"ticket-{interaction.user.name}".replace(" ", "-").lower()
        channel = await guild.create_text_channel(name=name, overwrites=overwrites, category=category, reason="ForgeBot ticket")
        await interaction.response.send_message(f"✅ Created {channel.mention}", ephemeral=True)
        await channel.send(embed=discord.Embed(title="Support Ticket", description="Explain your issue. Staff will be with you shortly.", color=discord.Color(MIDNIGHT)), view=CloseTicketView())

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge:close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds…", ephemeral=True)
        await interaction.channel.edit(archived=None)  # noop for non-threads
        await interaction.channel.delete(reason="ForgeBot close ticket")

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ticket_panel", description="Post the ticket panel with button")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        emb = discord.Embed(title="Need Help?", description="Press **Open Ticket** to create a private support channel.", color=discord.Color(MIDNIGHT))
        await interaction.response.send_message(embed=emb, view=TicketView())

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))

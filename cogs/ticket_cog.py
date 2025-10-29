
# cogs/ticket_cog.py
import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID") or 0)
TICKETS_CATEGORY_ID = int(os.getenv("TICKETS_CATEGORY_ID") or 0)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="forge_ticket_open")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Run this in a server.", ephemeral=True); return
        category = guild.get_channel(TICKETS_CATEGORY_ID) if TICKETS_CATEGORY_ID else None
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True),
        }
        staff_role = guild.get_role(STAFF_ROLE_ID) if STAFF_ROLE_ID else None
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel=True)

        name = f"ticket-{interaction.user.name}".lower()
        channel = await guild.create_text_channel(name=name[:90], category=category, overwrites=overwrites)
        await channel.send(
            content=f"{interaction.user.mention}" + (f" {staff_role.mention}" if staff_role else ""),
            embed=discord.Embed(title="Support Ticket", description="Describe your issue below.", color=discord.Color.blurple()),
            view=CloseView(channel.id)
        )
        await interaction.response.send_message(f"✅ Created {channel.mention}", ephemeral=True)

class CloseView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="✅ Close Ticket", style=discord.ButtonStyle.success, custom_id="forge_ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.channel or interaction.channel.id != self.channel_id:
            await interaction.response.send_message("Wrong channel.", ephemeral=True); return
        await interaction.response.send_message("🧹 Closing in 3 seconds…", ephemeral=True)
        await interaction.channel.send("Ticket will be closed by staff.")
        await interaction.channel.delete(reason=f"Closed by {interaction.user}")

class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ticket_panel", description="Post the ticket button (admins).")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction: discord.Interaction,
                           title: str = "Need Help?",
                           description: str = "Click the button to open a private ticket with staff."):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Posted ticket panel.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))

import os
import discord
from discord.ext import commands
from discord import app_commands

TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID", "0"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("SUPPORT_LOG_CHANNEL_ID", "0"))

OPEN_MSG = "👋 **Welcome to Support!**\nTell us what's going on and a staff member will be with you shortly."

class TicketOpen(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="forge_open_ticket")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        category = interaction.guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None
        if category is None or not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("⚠️ TICKET_CATEGORY_ID is misconfigured.", ephemeral=True)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True)
        }
        if STAFF_ROLE_ID:
            staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)

        channel = await category.create_text_channel(name=f"ticket-{interaction.user.name}".replace(" ", "-")[:90], overwrites=overwrites)
        embed = discord.Embed(title="Support Ticket", description=OPEN_MSG, color=0x5865F2)
        await channel.send(content=f"{interaction.user.mention}", embed=embed, view=TicketControls())
        await interaction.response.send_message(f"✅ Created {channel.mention}", ephemeral=True)

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close", style=discord.ButtonStyle.danger, custom_id="forge_close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("Archiving ticket…", ephemeral=True)
        try:
            await channel.edit(name=f"archived-{channel.name[:80]}", locked=True)
        except Exception:
            pass
        if LOG_CHANNEL_ID:
            log = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log:
                await log.send(f"🗄️ Ticket archived: {channel.name} by {interaction.user.mention}")
        # lock for everyone
        overwrites = channel.overwrites
        for target, perms in list(overwrites.items()):
            perms.send_messages = False
            overwrites[target] = perms
        await channel.edit(overwrites=overwrites)
        await channel.send("🗄️ This ticket has been archived. A mod can delete it when finished.")

class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketOpen())
        self.bot.add_view(TicketControls())

    @app_commands.command(name="setup-tickets", description="Post the ticket panel in this channel")
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Need Help?", description="Click the button below to open a private ticket with staff.", color=0x2f3136)
        await interaction.channel.send(embed=embed, view=TicketOpen())
        await interaction.response.send_message("✅ Posted ticket panel.", ephemeral=True)


import discord, os, io, datetime
from discord.ext import commands
from discord import app_commands

CATEGORY_ID = os.getenv("TICKET_CATEGORY_ID")
TRANSCRIPT_CHANNEL_ID = os.getenv("TRANSCRIPT_CHANNEL_ID")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Open Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket"))

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setup_persistent_views(self):
        self.bot.add_view(TicketView())

    @app_commands.command(name="ticketpanel", description="Send ticket panel")
    async def ticketpanel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Tickets", description="Open ticket below")
        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("Panel sent", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data.get("custom_id") == "open_ticket":
            cat = interaction.guild.get_channel(int(CATEGORY_ID))
            channel = await interaction.guild.create_text_channel(f"ticket-{interaction.user.name}", category=cat)
            await channel.send(f"{interaction.user.mention} ticket created.")
            await interaction.response.send_message("Ticket opened", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))

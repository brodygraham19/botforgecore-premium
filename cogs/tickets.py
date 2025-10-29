from __future__ import annotations
import os, discord
from discord.ext import commands
from discord import app_commands
from .helpers import get_role

MIDNIGHT = 0x0f172a

class CloseTicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge:close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing in 5 seconds…", ephemeral=True)
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        try: await interaction.channel.delete(reason="ForgeBot ticket closed")  # type: ignore
        except discord.Forbidden: await interaction.followup.send("I lack permission to delete this channel.", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="forge:open_ticket")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = interaction.guild
        if g is None: return await interaction.response.send_message("Use this in a server.", ephemeral=True)

        support_role = get_role(g, int(os.getenv("SUPPORT_ROLE_ID","0")), "Support Team")
        overwrites = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)

        category_id = int(os.getenv("TICKET_CATEGORY_ID","0"))
        category = g.get_channel(category_id) if category_id else None

        ch = await g.create_text_channel(
            name=f"ticket-{interaction.user.name}".lower()[:90],
            overwrites=overwrites, category=category, reason="ForgeBot ticket open"
        )
        emb = discord.Embed(title="Support Ticket", description="Explain your issue. Staff will be with you shortly.", colour=discord.Colour(MIDNIGHT))
        await ch.send(embed=emb, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Created {ch.mention}", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot): self.bot = bot

    @app_commands.command(name="ticket_panel", description="Post a ticket button panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        emb = discord.Embed(title="Need Help?", description="Press the button to open a private ticket with staff.", colour=discord.Colour(MIDNIGHT))
        await interaction.response.send_message(embed=emb, view=TicketView())

async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))

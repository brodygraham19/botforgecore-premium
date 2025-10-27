import discord, json, re
from discord.ext import commands
from discord import app_commands
with open("config.json","r") as f: CONFIG = json.load(f)
COLOR = int(CONFIG["theme_color_hex"].lstrip("#"),16)
def sanitize(s:str)->str: return re.sub(r'[^a-z0-9\-]','-',s.lower())[:90]
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket…", ephemeral=True); await interaction.channel.delete(reason="Ticket closed")
class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="🎟 Open Ticket", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = interaction.guild
        cat = discord.utils.get(g.categories, name=CONFIG["categories"]["tickets"]) or await g.create_category(CONFIG["categories"]["tickets"])
        base = f"ticket-{sanitize(interaction.user.name)}"; name = base; i=1
        while discord.utils.get(g.text_channels, name=name):
            i += 1; name = f"{base}-{i}"
        overwrites = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        mod_role = discord.utils.get(g.roles, name=CONFIG["roles"]["moderator"])
        if mod_role: overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        ch = await g.create_text_channel(name, category=cat, overwrites=overwrites, reason="Ticket created via panel")
        e = discord.Embed(title="New Ticket", description=f"Opened by {interaction.user.mention}", color=COLOR)
        if mod_role: await ch.send(mod_role.mention, embed=e, view=CloseView())
        else: await ch.send(embed=e, view=CloseView())
        await interaction.response.send_message(f"Ticket created: {ch.mention}", ephemeral=True)
class TicketButtonCog(commands.Cog):
    def __init__(self, bot): self.bot = bot
    @app_commands.command(description="Post the Ticket button panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticketpanel(self, interaction: discord.Interaction):
        e = discord.Embed(title="Need Help?", description="Click to open a private ticket with staff.", color=COLOR)
        e.set_thumbnail(url=CONFIG["logo_url"]); await interaction.response.send_message(embed=e, view=TicketView())
async def setup(bot): await bot.add_cog(TicketButtonCog(bot))

import discord, json, re
from discord.ext import commands
from discord import app_commands

with open("config.json", "r") as f:
    CONFIG = json.load(f)

COLOR = int(CONFIG["theme_color_hex"].replace("#", ""), 16)

def sanitize(name: str) -> str:
    return re.sub(r'[^a-z0-9\-]', '-', name.lower())[:90]

class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await interaction.channel.delete(reason="Ticket closed")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎟 Open Ticket", style=discord.ButtonStyle.primary)
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        cat_name = CONFIG["categories"]["tickets"]
        category = discord.utils.get(guild.categories, name=cat_name)
        if not category:
            category = await guild.create_category(cat_name)

        chan_name = f"ticket-{sanitize(interaction.user.name)}"
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
            overwrites[mod_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(chan_name, overwrites=overwrites, category=category)
        e = discord.Embed(title="New Ticket", description=f"Opened by {interaction.user.mention}", color=COLOR)
        await channel.send(content=mod_role.mention if mod_role else None, embed=e, view=CloseView())
        await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

class TicketButtonCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Post the ticket creation button panel")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticketpanel(self, interaction: discord.Interaction):
        e = discord.Embed(
            title="Need Help?",
            description="Click below to open a private ticket with staff.",
            color=COLOR
        )
        e.set_thumbnail(url=CONFIG["logo_url"])
        view = TicketView()
        await interaction.response.send_message(embed=e, view=view)

async def setup(bot):
    await bot.add_cog(TicketButtonCog(bot))
# ForgeBot Core (Verify + Ticket System)
# Works with discord.py 2.4.x and Railway hosting

import os
import asyncio
import discord
from discord import app_commands, Interaction, Embed
from discord.ui import View, Button, button

# ---------------------------------
# ⚙️ CONFIG SETTINGS
# ---------------------------------
EMBED_COLOR = discord.Color.from_rgb(15, 25, 45)  # midnight blue
ROLE_NAMES = [
    "Owner",
    "admin",
    "Forge Bot",
    "Ticket Support",
    "Customer",
    "Member",
    "Verified",
    "VIP",
    "Server Booster",
    "Quarantine",
    "Bot",
]
VERIFY_ROLE = "Verified"
QUARANTINE_ROLE = "Quarantine"
TICKET_SUPPORT_ROLE = "Ticket Support"
TICKETS_CATEGORY = "Support Tickets"
VERIFY_CHANNEL = "verify"
TICKETS_CHANNEL = "tickets"

# ---------------------------------
# 🔌 SETUP BOT
# ---------------------------------
intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ---------------------------------
# 🟢 VERIFY BUTTON
# ---------------------------------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Verify", style=discord.ButtonStyle.success, custom_id="forge_verify_btn")
    async def verify(self, _btn: Button, interaction: Interaction):
        guild = interaction.guild
        verify_role = discord.utils.get(guild.roles, name=VERIFY_ROLE)
        quarantine_role = discord.utils.get(guild.roles, name=QUARANTINE_ROLE)

        if not verify_role:
            await interaction.response.send_message(
                f"❗ The **{VERIFY_ROLE}** role doesn’t exist yet. Run `/build` first.",
                ephemeral=True,
            )
            return

        added, removed = False, False
        if verify_role not in interaction.user.roles:
            await interaction.user.add_roles(verify_role)
            added = True

        if quarantine_role and quarantine_role in interaction.user.roles:
            await interaction.user.remove_roles(quarantine_role)
            removed = True

        msg = "✅ Verified!"
        if added or removed:
            msg += f" (Added: {VERIFY_ROLE})"
        await interaction.response.send_message(msg, ephemeral=True)

# ---------------------------------
# 🎟️ TICKET BUTTONS
# ---------------------------------
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge_close_ticket")
    async def close_ticket(self, _btn: Button, interaction: Interaction):
        await interaction.response.send_message("Closing ticket... 🔒", ephemeral=True)
        await asyncio.sleep(1)
        await interaction.channel.delete(reason=f"Closed by {interaction.user}")

class TicketPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="forge_create_ticket")
    async def create_ticket(self, _btn: Button, interaction: Interaction):
        guild = interaction.guild
        support_role = discord.utils.get(guild.roles, name=TICKET_SUPPORT_ROLE)
        if not support_role:
            await interaction.response.send_message(
                f"❗ The **{TICKET_SUPPORT_ROLE}** role doesn’t exist yet. Run `/build` first.",
                ephemeral=True,
            )
            return

        category = discord.utils.get(guild.categories, name=TICKETS_CATEGORY)
        if not category:
            category = await guild.create_category(TICKETS_CATEGORY, reason="ForgeBot Ticket System")

        base_name = f"ticket-{interaction.user.name.lower().replace(' ', '-')}"
        name = base_name
        i = 1
        while discord.utils.get(guild.channels, name=name):
            i += 1
            name = f"{base_name}-{i}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel = await guild.create_text_channel(name=name, category=category, overwrites=overwrites)
        embed = Embed(title="🎟️ Support Ticket", description="A staff member will assist you shortly.", color=EMBED_COLOR)
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"📨 Ticket created: {channel.mention}", ephemeral=True)

# ---------------------------------
# 🧱 /BUILD COMMAND
# ---------------------------------
@tree.command(name="build", description="Create roles, channels, and post verify/ticket panels (admin only).")
@app_commands.checks.has_permissions(manage_guild=True)
async def build(interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    g = interaction.guild

    # Ensure roles exist
    for name in ROLE_NAMES:
        if not discord.utils.get(g.roles, name=name):
            await g.create_role(name=name, reason="ForgeBot setup")

    await interaction.followup.send("✅ Roles created or already exist.")

    # Create channels if missing
    verify_channel = discord.utils.get(g.text_channels, name=VERIFY_CHANNEL)
    tickets_channel = discord.utils.get(g.text_channels, name=TICKETS_CHANNEL)

    if not verify_channel:
        verify_channel = await g.create_text_channel(VERIFY_CHANNEL, reason="ForgeBot setup")
    if not tickets_channel:
        tickets_channel = await g.create_text_channel(TICKETS_CHANNEL, reason="ForgeBot setup")

    # Send panels
    verify_embed = Embed(title="✅ Verify Here", description="Click the button below to verify yourself.", color=EMBED_COLOR)
    await verify_channel.send(embed=verify_embed, view=VerifyView())

    ticket_embed = Embed(title="🎟️ Need Help?", description="Click below to create a support ticket.", color=EMBED_COLOR)
    await tickets_channel.send(embed=ticket_embed, view=TicketPanelView())

    await interaction.followup.send("✅ Setup complete! Verify & Ticket panels created.", ephemeral=True)

# ---------------------------------
# 🚀 ON READY
# ---------------------------------
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())

    try:
        synced = await tree.sync()
        print(f"Slash commands synced: {len(synced)} command(s)")
    except Exception as e:
        print(f"Slash sync error: {e}")

    print(f"✅ Logged in as {bot.user}")

# ---------------------------------
# ▶️ START
# ---------------------------------
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    if not TOKEN:
        raise ValueError("Missing DISCORD_BOT_TOKEN in environment!")
    bot.run(TOKEN)

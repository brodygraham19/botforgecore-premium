# bot.py — ForgeBot (verify + tickets + auto-builder)
# discord.py 2.4.x

import os
import asyncio
import discord
from discord import app_commands, Interaction, Embed
from discord.ui import View, Button, button

# ---------- Config you can change ----------
EMBED_COLOR = discord.Color.from_rgb(10, 20, 35)  # midnight blue
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
CLOSED_TICKETS_CATEGORY = "Closed Tickets"
VERIFY_CHANNEL = "verify"
TICKETS_CHANNEL = "tickets"
# ------------------------------------------

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ---------- Verify Button ----------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Verify", style=discord.ButtonStyle.success, custom_id="forge_verify_btn")
    async def verify(self, _btn: Button, interaction: Interaction):
        guild = interaction.guild
        vr = discord.utils.get(guild.roles, name=VERIFY_ROLE)
        qr = discord.utils.get(guild.roles, name=QUARANTINE_ROLE)
        if vr is None:
            await interaction.response.send_message(
                f"❗ The **{VERIFY_ROLE}** role doesn’t exist yet. Run **/build** first.",
                ephemeral=True,
            )
            return

        changes = []
        if vr not in interaction.user.roles:
            await interaction.user.add_roles(vr, reason="ForgeBot verify")
            changes.append(f"✅ Added **{VERIFY_ROLE}**")

        if qr and qr in interaction.user.roles:
            await interaction.user.remove_roles(qr, reason="ForgeBot verify")
            changes.append(f"🧹 Removed **{QUARANTINE_ROLE}**")

        if changes:
            await interaction.response.send_message("\n".join(changes), ephemeral=True)
        else:
            await interaction.response.send_message("You’re already verified ✅", ephemeral=True)


# ---------- Ticket Buttons ----------
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge_close_ticket")
    async def close(self, _btn: Button, interaction: Interaction):
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Closing… 🔒", ephemeral=True)
            await asyncio.sleep(1)
            await interaction.channel.delete(reason=f"Closed by {interaction.user}")


class TicketPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="forge_create_ticket")
    async def create_ticket(self, _btn: Button, interaction: Interaction):
        guild = interaction.guild
        support_role = discord.utils.get(guild.roles, name=TICKET_SUPPORT_ROLE)
        if support_role is None:
            await interaction.response.send_message(
                f"❗ The **{TICKET_SUPPORT_ROLE}** role doesn’t exist yet. Run **/build** first.",
                ephemeral=True,
            )
            return

        cat = discord.utils.get(guild.categories, name=TICKETS_CATEGORY)
        if cat is None:
            cat = await guild.create_category(TICKETS_CATEGORY, reason="ForgeBot: create tickets category")

        safe_name = interaction.user.name.lower().replace(" ", "-")
        base = f"ticket-{safe_name}"
        name = base
        i = 1
        while discord.utils.get(guild.channels, name=name):
            i += 1
            name = f"{base}-{i}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel = await guild.create_text_channel(name=name, category=cat, overwrites=overwrites)
        embed = Embed(title="Support Ticket", description="A team member will assist you shortly.", color=EMBED_COLOR)
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"📨 Created {channel.mention}", ephemeral=True)


# ---------- /build Command ----------
@tree.command(name="build", description="Create roles, channels, and post verify/ticket panels (admin only).")
@app_commands.checks.has_permissions(manage_guild=True)
async def build(interaction: Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)
    g = interaction.guild
    for name in ROLE_NAMES:
        if not discord.utils.get(g.roles, name=name):
            await g.create_role(name=name, reason="ForgeBot /build")
    await interaction.followup.send("✅ Roles ensured. Building channels...")

    # Verify & Ticket channels
    for ch_name in [VERIFY_CHANNEL, TICKETS_CHANNEL]:
        if not discord.utils.get(g.text_channels, name=ch_name):
            await g.create_text_channel(name=ch_name, reason="ForgeBot /build")

    vchan = discord.utils.get(g.text_channels, name=VERIFY_CHANNEL)
    tchan = discord.utils.get(g.text_channels, name=TICKETS_CHANNEL)

    if vchan:
        embed = Embed(title="Verify", description="Press **Verify** to access the server.", color=EMBED_COLOR)
        await vchan.send(embed=embed, view=VerifyView())

    if tchan:
        embed = Embed(title="Tickets", description="Press **Create Ticket** for help.", color=EMBED_COLOR)
        await tchan.send(embed=embed, view=TicketPanelView())

    await interaction.followup.send("✅ ForgeBot build complete.", ephemeral=True)


# ---------- Bot lifecycle ----------
@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketPanelView())
    bot.add_view(CloseTicketView())
    await tree.sync()
    print(f"Logged in as {bot.user} (ready)")


if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(TOKEN)

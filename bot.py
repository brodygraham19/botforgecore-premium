# ForgeBotCore Premium (Build B) - Midnight/Skull theme
# Features in this file:
# - /build : creates categories/channels/permissions + posts Verify & Ticket panels
# - Verify button: adds "Verified", removes "Quarantine"
# - Ticket system: "Create Ticket" + "Close Ticket" buttons
# - /verifysetup and /ticketsetup to re-post panels anywhere
# - Minimal logs to #botforge-logs
#
# Requires: discord.py==2.4.0, python-dotenv==1.0.1 (optional)
# Env var: DISCORD_BOT_TOKEN
#
# IMPORTANT: Enable "SERVER MEMBERS INTENT" in the bot's Dev Portal.

import os
import asyncio
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

# ---------- Config ----------
GUILD_LOG_CHANNEL_NAME = "botforge-logs"
TICKET_CATEGORY_NAME = "🎟・Support Tickets"
TICKET_SUPPORT_ROLE = "Ticket Support"
VERIFIED_ROLE = "Verified"
QUARANTINE_ROLE = "Quarantine"

EMBED_COLOR = discord.Color.dark_blue()
EMBED_FOOTER = "BotForge • midnight skull"

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("forgebot")

# ---------- Bot Setup ----------
intents = discord.Intents.default()
intents.members = True  # REQUIRED for role add/remove
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ---------- Helpers ----------
async def get_or_create_role(guild: discord.Guild, name: str, **kwargs) -> discord.Role:
    role = discord.utils.get(guild.roles, name=name)
    if role is None:
        role = await guild.create_role(name=name, **kwargs, reason=f"Auto-create role: {name}")
    return role


async def get_or_create_text_channel(
    guild: discord.Guild,
    name: str,
    category: Optional[discord.CategoryChannel] = None,
    overwrites: Optional[dict] = None,
) -> discord.TextChannel:
    ch = discord.utils.get(guild.text_channels, name=name)
    if ch is None:
        ch = await guild.create_text_channel(name=name, category=category, overwrites=overwrites)
    return ch


async def get_or_create_category(guild: discord.Guild, name: str, overwrites: Optional[dict] = None):
    cat = discord.utils.get(guild.categories, name=name)
    if cat is None:
        cat = await guild.create_category(name=name, overwrites=overwrites)
    return cat


async def log_to_channel(guild: discord.Guild, message: str):
    ch = discord.utils.get(guild.text_channels, name=GUILD_LOG_CHANNEL_NAME)
    if ch:
        try:
            await ch.send(message)
        except Exception:
            pass


def skull_embed(title: str, description: str = "", *, color: Optional[discord.Color] = None):
    c = color or EMBED_COLOR
    e = discord.Embed(title=f"💀 {title}", description=description, color=c)
    e.set_footer(text=EMBED_FOOTER)
    return e


# ---------- PERSISTENT VIEWS ----------
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, custom_id="forge:verify")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("Guild not found.", ephemeral=True)

        verified = discord.utils.get(guild.roles, name=VERIFIED_ROLE)
        quarantine = discord.utils.get(guild.roles, name=QUARANTINE_ROLE)

        if verified is None:
            verified = await guild.create_role(name=VERIFIED_ROLE, reason="Auto-create Verified role")
        # Add role & remove quarantine
        try:
            await interaction.user.add_roles(verified, reason="User verified")
            if quarantine and quarantine in interaction.user.roles:
                await interaction.user.remove_roles(quarantine, reason="Verified")
        except discord.Forbidden:
            return await interaction.response.send_message("I need Manage Roles and to be above those roles.", ephemeral=True)

        await interaction.response.send_message(embed=skull_embed("Verified!", "Welcome in 🎉"), ephemeral=True)
        await log_to_channel(guild, f"✅ **{interaction.user}** verified.")


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge:ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        ch = interaction.channel
        if isinstance(ch, discord.TextChannel) and ch.name.startswith("ticket-"):
            await interaction.response.send_message("Closing this ticket in 3 seconds…", ephemeral=True)
            await asyncio.sleep(3)
            try:
                await ch.delete(reason=f"Closed by {interaction.user}")
            except discord.Forbidden:
                await interaction.followup.send("I don't have permission to delete this channel.", ephemeral=True)
        else:
            await interaction.response.send_message("This isn't a ticket channel.", ephemeral=True)


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, custom_id="forge:ticket_create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("Guild not found.", ephemeral=True)

        cat = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        if cat is None:
            return await interaction.response.send_message("Ticket category missing. Ask an admin to run `/build` first.", ephemeral=True)

        # One ticket per user
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.id}")
        if existing is not None:
            return await interaction.response.send_message(f"You already have a ticket: {existing.mention}", ephemeral=True)

        # Permissions
        everyone = guild.default_role
        support = discord.utils.get(guild.roles, name=TICKET_SUPPORT_ROLE)
        if support is None:
            support = await guild.create_role(name=TICKET_SUPPORT_ROLE, reason="Auto-create Ticket Support role")

        overwrites = {
            everyone: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True),
            support: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)
        }

        ch = await guild.create_text_channel(f"ticket-{interaction.user.id}", category=cat, overwrites=overwrites, reason="New support ticket")
        await ch.send(content=f"{support.mention} | Ticket opened by {interaction.user.mention}", embed=skull_embed("Support Ticket", "Describe your issue below. Use the button to close."), view=CloseTicketView())
        await interaction.response.send_message(f"Ticket created: {ch.mention}", ephemeral=True)
        await log_to_channel(guild, f"🎟️ Ticket opened by **{interaction.user}** → {ch.mention}")


# ---------- Auto Builder ----------
async def run_auto_builder(guild: discord.Guild):
    everyone = guild.default_role

    # Roles
    verified = await get_or_create_role(guild, VERIFIED_ROLE)
    quarantine = await get_or_create_role(guild, QUARANTINE_ROLE)
    support = await get_or_create_role(guild, TICKET_SUPPORT_ROLE)

    # Categories (default: private to everyone)
    deny_all = {everyone: discord.PermissionOverwrite(view_channel=False)}
    cat_welcome = await get_or_create_category(guild, "server", overwrites=deny_all)
    cat_important = await get_or_create_category(guild, "📢・important", overwrites=deny_all)
    cat_ticket = await get_or_create_category(guild, "🎟・ticketing & purchasing", overwrites=deny_all)
    cat_lounge = await get_or_create_category(guild, "💬・lounge", overwrites=deny_all)
    cat_staff = await get_or_create_category(guild, "🛡・staff", overwrites=deny_all)
    cat_voice = await get_or_create_category(guild, "🔊・voice", overwrites=deny_all)

    # Channel permissions shortcuts
    allow_verified = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        verified: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True, embed_links=True),
    }
    verify_only = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        quarantine: discord.PermissionOverwrite(send_messages=True),
        verified: discord.PermissionOverwrite(view_channel=False)  # Hide for verified if you like; set to True if you want them to still see it
    }

    # server (welcome / verify / portal)
    ch_welcome = await get_or_create_text_channel(guild, "welcome", category=cat_welcome, overwrites=allow_verified)
    ch_verify  = await get_or_create_text_channel(guild, "verify",  category=cat_welcome, overwrites=verify_only)
    ch_portal  = await get_or_create_text_channel(guild, "portal",  category=cat_welcome, overwrites=allow_verified)

    # important
    await get_or_create_text_channel(guild, "announcements", category=cat_important, overwrites=allow_verified)
    await get_or_create_text_channel(guild, "status",        category=cat_important, overwrites=allow_verified)
    await get_or_create_text_channel(guild, "giveaways",     category=cat_important, overwrites=allow_verified)

    # tickets
    ticket_cat = await get_or_create_category(guild, TICKET_CATEGORY_NAME, overwrites=deny_all)
    tickets_panel = await get_or_create_text_channel(guild, "tickets", category=ticket_cat, overwrites=allow_verified)
    await get_or_create_text_channel(guild, "reviews", category=cat_ticket, overwrites=allow_verified)
    await get_or_create_text_channel(guild, "website", category=cat_ticket, overwrites=allow_verified)

    # lounge
    await get_or_create_text_channel(guild, "chat",                 category=cat_lounge, overwrites=allow_verified)
    await get_or_create_text_channel(guild, "motivational-quotes",  category=cat_lounge, overwrites=allow_verified)

    # staff
    await get_or_create_text_channel(guild, "mod-logs",            category=cat_staff, overwrites={everyone: discord.PermissionOverwrite(view_channel=False), support: discord.PermissionOverwrite(view_channel=True)})
    await get_or_create_text_channel(guild, "ticket-transcripts",  category=cat_staff, overwrites={everyone: discord.PermissionOverwrite(view_channel=False), support: discord.PermissionOverwrite(view_channel=True)})
    await get_or_create_text_channel(guild, "verify-logs",         category=cat_staff, overwrites={everyone: discord.PermissionOverwrite(view_channel=False)})
    logs = await get_or_create_text_channel(guild, GUILD_LOG_CHANNEL_NAME, category=cat_staff, overwrites={everyone: discord.PermissionOverwrite(view_channel=False)})

    # voice
    if not discord.utils.get(guild.voice_channels, name="VC"):
        await guild.create_voice_channel("VC", category=cat_voice, overwrites=allow_verified)

    # Post panels
    try:
        await ch_verify.send(embed=skull_embed("Verify to Enter", "Press **Verify** below to unlock the server."), view=VerifyView())
    except Exception:
        pass

    try:
        await tickets_panel.send(embed=skull_embed("Open a Ticket", "For support, press **Create Ticket**."), view=TicketPanelView())
    except Exception:
        pass

    await log_to_channel(guild, "🛠️ Auto-builder finished.")


# ---------- Slash Commands ----------
@tree.command(name="build", description="(Admin) Build channels, roles, and post panels")
@app_commands.default_permissions(administrator=True)
async def build_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(embed=skull_embed("Building…", "Stand by while I set everything up."), ephemeral=True)
    await run_auto_builder(interaction.guild)


@tree.command(name="verifysetup", description="(Admin) Post the verify button panel here")
@app_commands.default_permissions(manage_guild=True)
async def verifysetup(interaction: discord.Interaction):
    await interaction.response.send_message("Panel posted.", ephemeral=True)
    await interaction.channel.send(embed=skull_embed("Verify to Enter", "Press **Verify** below to unlock the server."), view=VerifyView())


@tree.command(name="ticketsetup", description="(Admin) Post the ticket panel here")
@app_commands.default_permissions(manage_guild=True)
async def ticketsetup(interaction: discord.Interaction):
    await interaction.response.send_message("Panel posted.", ephemeral=True)
    await interaction.channel.send(embed=skull_embed("Open a Ticket", "For support, press **Create Ticket**."), view=TicketPanelView())


# ---------- Events ----------
@bot.event
async def on_ready():
    # Register persistent views so old buttons keep working after restarts
    bot.add_view(VerifyView())
    bot.add_view(CloseTicketView())
    bot.add_view(TicketPanelView())

    try:
        await tree.sync()
        log.info("Slash commands synced.")
    except Exception as e:
        log.exception("Slash sync error: %s", e)

    log.info("Logged in as %s", bot.user)


# ---------- Entrypoint ----------
def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Environment variable DISCORD_BOT_TOKEN is missing.")
    bot.run(token)


if __name__ == "__main__":
    main()

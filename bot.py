# ForgeBot Auto‑Builder (Verify + Ticket System Only)
# Discord.py v2.4 — persistent buttons, slash commands, and idempotent setup
# Theme: Midnight Skull (dark blue embeds)
#
# Commands:
#   /build                 -> (Admin) Create roles, categories, channels, and post panels
#   /repost_panels         -> (Admin) Repost verify & ticket panels in the current channel
#   /announce message:"..."-> (Admin) Send an announcement embed
#   /rules                 -> Show the rules embed
#   /help                  -> Show command help
#   /ping                  -> Latency check
#
# Panels:
#   ✅ Verify button -> adds "Verified" role and DM/ephemeral confirmation
#   🎫 Create Ticket -> creates a private channel with staff+user
#
# NOTE: Put your bot token in an environment variable DISCORD_BOT_TOKEN
#       or a local .env file "DISCORD_BOT_TOKEN=xxxxx"

import os
import asyncio
import datetime as dt
from typing import Dict, Optional

import discord
from discord import app_commands, ui, ButtonStyle, Interaction, Embed, Permissions, Colour
from discord.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional in hosted environments
    pass

# ------------------------------
# Configuration
# ------------------------------
GUILD_TEMPLATE_NAME = "BotForge Core"
THEME_COLOR = Colour.dark_blue()
SKULL = "💀"
TICKET_EMOJI = "🎫"
CHECK_EMOJI = "✅"

VERIFY_ROLE_NAME = "Verified"
TICKET_SUPPORT_ROLE = "Ticket Support"
ADMIN_ROLE = "admin"
OWNER_ROLE = "Owner"
BOT_ROLE = "Bot"
MEMBER_ROLE = "Member"

# Categories / Channels
CAT_WELCOME = "welcome"
CHAN_PORTAL = "portal"
CHAN_VERIFY = "verify"

CAT_IMPORTANT = "important"
CHAN_ANNOUNCE = "announcements"
CHAN_STATUS = "status"
CHAN_GIVEAWAYS = "giveaways"

CAT_TICKETS = "Ticketing & Purchasing"
CHAN_TICKETS = "tickets"
CHAN_REVIEWS = "reviews"
CHAN_WEBSITE = "website"

CAT_LOGS = "Staff"
CHAN_MOD_LOGS = "mod-logs"
CHAN_TICKET_TRANSCRIPTS = "ticket-transcripts"
CHAN_VERIFY_LOGS = "verify-logs"
CHAN_SELLAUTH = "sellauth-logs"  # optional placeholder

CAT_SUPPORT_TICKETS = "Support Tickets"  # for open ticket channels
CHAN_CLOSED_TICKETS = "Closed Tickets"   # category for archived/closed tickets


# ------------------------------
# Utility helpers
# ------------------------------
def blue_embed(title: str, description: str = "", footer: Optional[str] = None) -> Embed:
    e = Embed(title=f"{SKULL} {title}", description=description, color=THEME_COLOR)
    e.timestamp = dt.datetime.utcnow()
    if footer:
        e.set_footer(text=footer)
    return e


async def get_or_create_role(guild: discord.Guild, name: str, *, colour: Optional[Colour] = None,
                             perms: Optional[Permissions] = None, hoist: bool = False,
                             mentionable: bool = True) -> discord.Role:
    role = discord.utils.get(guild.roles, name=name)
    if role:
        # update basic properties if supplied
        try:
            await role.edit(colour=colour or role.colour,
                            permissions=perms or role.permissions,
                            hoist=hoist if hoist is not None else role.hoist,
                            mentionable=mentionable if mentionable is not None else role.mentionable,
                            reason="ForgeBot auto‑builder sync")
        except Exception:
            pass
        return role
    return await guild.create_role(
        name=name, colour=colour or THEME_COLOR,
        permissions=perms or Permissions.none(),
        hoist=hoist, mentionable=mentionable, reason="ForgeBot auto‑builder create role"
    )


async def get_or_create_category(guild: discord.Guild, name: str, *, position: Optional[int] = None) -> discord.CategoryChannel:
    cat = discord.utils.get(guild.categories, name=name)
    if cat:
        if position is not None:
            try:
                await cat.edit(position=position, reason="ForgeBot category position sync")
            except Exception:
                pass
        return cat
    return await guild.create_category(name=name, position=position)


async def get_or_create_text(guild: discord.Guild, category: discord.CategoryChannel, name: str,
                             *, overwrites: Optional[Dict] = None, topic: Optional[str] = None,
                             slowmode: int = 0) -> discord.TextChannel:
    ch = discord.utils.get(category.text_channels, name=name)
    if ch:
        try:
            await ch.edit(topic=topic, slowmode_delay=slowmode,
                          overwrites=overwrites or ch.overwrites,
                          reason="ForgeBot channel sync")
        except Exception:
            pass
        return ch
    return await guild.create_text_channel(name=name, category=category,
                                           overwrites=overwrites, topic=topic,
                                           slowmode_delay=slowmode)


def staff_or_admin(user: discord.Member) -> bool:
    names = {r.name for r in user.roles}
    return (user.guild_permissions.administrator
            or ADMIN_ROLE in names
            or TICKET_SUPPORT_ROLE in names
            or OWNER_ROLE in names)


# ------------------------------
# Persistent Views (Buttons)
# ------------------------------
VERIFY_CUSTOM_ID = "forge_verify_btn"
TICKET_CUSTOM_ID = "forge_ticket_btn"
CLOSE_TICKET_CUSTOM_ID = "forge_close_btn"


class VerifyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            ui.Button(label="Verify", emoji=CHECK_EMOJI, style=ButtonStyle.success, custom_id=VERIFY_CUSTOM_ID)
        )

    @ui.button(label="hidden", style=ButtonStyle.success)
    async def _dummy(self, *_):  # never shown (placeholder to satisfy type checker)
        pass

    @discord.ui.button  # not used; we handle in on_interaction below (custom_id)
    async def _unused(self, *_):
        pass


class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            ui.Button(label="Create Ticket", emoji=TICKET_EMOJI, style=ButtonStyle.primary, custom_id=TICKET_CUSTOM_ID)
        )

    @ui.button(label="hidden", style=ButtonStyle.primary)
    async def _dummy(self, *_):
        pass


class CloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            ui.Button(label="Close Ticket", emoji="🔒", style=ButtonStyle.danger, custom_id=CLOSE_TICKET_CUSTOM_ID)
        )

# ------------------------------
# Bot Setup
# ------------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    # Persistent views so buttons still work after restart
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseView())

    # Try to sync slash commands
    try:
        await tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print(f"Slash sync error: {e}")

    print(f"Logged in as {bot.user}")

# ------------------------------
# Auto‑builder
# ------------------------------
async def run_builder(guild: discord.Guild):
    # Create/update roles
    everyone = guild.default_role
    verified = await get_or_create_role(guild, VERIFY_ROLE_NAME)
    support = await get_or_create_role(guild, TICKET_SUPPORT_ROLE)
    admin = await get_or_create_role(guild, ADMIN_ROLE, perms=Permissions(administrator=True))
    owner = await get_or_create_role(guild, OWNER_ROLE, perms=Permissions(administrator=True))
    bot_role = await get_or_create_role(guild, BOT_ROLE)
    member_role = await get_or_create_role(guild, MEMBER_ROLE)

    # Category: welcome
    cat_welcome = await get_or_create_category(guild, CAT_WELCOME, position=0)

    # Overwrites
    portal_over = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        verified: discord.PermissionOverwrite(view_channel=True, send_messages=False),
    }
    verify_over = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }

    # Channels in welcome
    ch_portal = await get_or_create_text(guild, cat_welcome, CHAN_PORTAL,
                                         overwrites=portal_over,
                                         topic="Server portal & verification entry point")
    ch_verify = await get_or_create_text(guild, cat_welcome, CHAN_VERIFY,
                                         overwrites=verify_over,
                                         topic="Press the button to get Verified")

    # Category: important
    cat_imp = await get_or_create_category(guild, CAT_IMPORTANT, position=1)
    await get_or_create_text(guild, cat_imp, CHAN_ANNOUNCE, topic="Server announcements")
    await get_or_create_text(guild, cat_imp, CHAN_STATUS, topic="Status & updates")
    await get_or_create_text(guild, cat_imp, CHAN_GIVEAWAYS, topic="Giveaways")

    # Category: tickets
    cat_tickets = await get_or_create_category(guild, CAT_TICKETS, position=2)
    t_over = {
        everyone: discord.PermissionOverwrite(view_channel=True, send_messages=False),
        verified: discord.PermissionOverwrite(view_channel=True, send_messages=False),
    }
    ch_tickets = await get_or_create_text(guild, cat_tickets, CHAN_TICKETS,
                                          overwrites=t_over,
                                          topic="Press the button to open a ticket")
    await get_or_create_text(guild, cat_tickets, CHAN_REVIEWS, topic="Customer reviews")
    await get_or_create_text(guild, cat_tickets, CHAN_WEBSITE, topic="Links / Website")

    # Categories for logs & tickets
    cat_logs = await get_or_create_category(guild, CAT_LOGS, position=3)
    staff_over = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        support: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        admin: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        owner: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    await get_or_create_text(guild, cat_logs, CHAN_MOD_LOGS, overwrites=staff_over, topic="Moderation logs")
    await get_or_create_text(guild, cat_logs, CHAN_TICKET_TRANSCRIPTS, overwrites=staff_over, topic="Ticket transcripts")
    await get_or_create_text(guild, cat_logs, CHAN_VERIFY_LOGS, overwrites=staff_over, topic="Verify logs")
    await get_or_create_text(guild, cat_logs, CHAN_SELLAUTH, overwrites=staff_over, topic="3rd‑party logs")

    # Create ticket categories
    await get_or_create_category(guild, CAT_SUPPORT_TICKETS, position=4)
    await get_or_create_category(guild, CHAN_CLOSED_TICKETS, position=5)

    # Post panels
    await post_verify_panel(ch_portal)
    await post_ticket_panel(ch_tickets)


async def post_verify_panel(channel: discord.TextChannel):
    await channel.send(
        embed=blue_embed("Welcome to BotForge", "Press the button below to verify and unlock the forge 🔓"),
        view=VerifyView()
    )


async def post_ticket_panel(channel: discord.TextChannel):
    await channel.send(
        embed=blue_embed("Support & Purchasing", "Open a private ticket to contact staff."),
        view=TicketView()
    )


# ------------------------------
# Interaction handlers (buttons)
# ------------------------------
@bot.event
async def on_interaction(interaction: Interaction):
    if not interaction.type == discord.InteractionType.component:
        return

    cid = interaction.data.get("custom_id")

    # VERIFY
    if cid == VERIFY_CUSTOM_ID:
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("This only works in a server.", ephemeral=True)

        role = discord.utils.get(guild.roles, name=VERIFY_ROLE_NAME)
        if not role:
            role = await guild.create_role(name=VERIFY_ROLE_NAME, colour=THEME_COLOR)

        member = interaction.user if isinstance(interaction.user, discord.Member) else guild.get_member(interaction.user.id)
        if role in member.roles:
            return await interaction.response.send_message("You're already verified ✅", ephemeral=True)

        await member.add_roles(role, reason="ForgeBot verify")
        await interaction.response.send_message("You've been verified and granted access. Welcome!", ephemeral=True)

        # Log
        log = discord.utils.get(guild.text_channels, name=CHAN_VERIFY_LOGS)
        if log:
            await log.send(embed=blue_embed("User Verified", f"{member.mention} has verified."))

    # CREATE TICKET
    elif cid == TICKET_CUSTOM_ID:
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("This only works in a server.", ephemeral=True)

        user = interaction.user if isinstance(interaction.user, discord.Member) else guild.get_member(interaction.user.id)

        support_role = discord.utils.get(guild.roles, name=TICKET_SUPPORT_ROLE)
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE)
        owner_role = discord.utils.get(guild.roles, name=OWNER_ROLE)

        parent = discord.utils.get(guild.categories, name=CAT_SUPPORT_TICKETS)
        if parent is None:
            parent = await guild.create_category(CAT_SUPPORT_TICKETS)

        # unique channel name
        base = f"ticket-{user.name}".replace(" ", "-").lower()
        name = base
        i = 1
        while discord.utils.get(parent.text_channels, name=name):
            i += 1
            name = f"{base}-{i}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        for r in (support_role, admin_role, owner_role):
            if r:
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ch = await guild.create_text_channel(name, category=parent, overwrites=overwrites,
                                             topic=f"Support ticket for {user}",
                                             reason="ForgeBot open ticket")
        await ch.send(content=user.mention, embed=blue_embed("Ticket Created", "Staff will be with you shortly."), view=CloseView())
        await interaction.response.send_message(f"Created {ch.mention}", ephemeral=True)

        # Log
        log = discord.utils.get(guild.text_channels, name=CHAN_MOD_LOGS)
        if log:
            await log.send(embed=blue_embed("Ticket Opened", f"{user.mention} opened {ch.mention}"))

    # CLOSE TICKET
    elif cid == CLOSE_TICKET_CUSTOM_ID:
        guild = interaction.guild
        if not guild:
            return

        ch = interaction.channel
        if not isinstance(ch, discord.TextChannel):
            return

        member = interaction.user if isinstance(interaction.user, discord.Member) else guild.get_member(interaction.user.id)
        if not staff_or_admin(member):
            return await interaction.response.send_message("Only staff can close tickets.", ephemeral=True)

        archive = discord.utils.get(guild.categories, name=CHAN_CLOSED_TICKETS)
        if not archive:
            archive = await guild.create_category(CHAN_CLOSED_TICKETS)

        await interaction.response.send_message("Closing ticket…")
        try:
            await ch.edit(category=archive, reason="ForgeBot close ticket")
        except Exception:
            pass

        # Log
        log = discord.utils.get(guild.text_channels, name=CHAN_TICKET_TRANSCRIPTS)
        if log:
            await log.send(embed=blue_embed("Ticket Closed", f"{ch.mention} was closed by {member.mention}"))


# ------------------------------
# Slash Commands
# ------------------------------
@tree.command(name="ping", description="Check if the bot is online")
async def ping_cmd(inter: Interaction):
    await inter.response.send_message(f"Pong! `{round(bot.latency*1000)}ms`", ephemeral=True)


@tree.command(name="help", description="Show help for ForgeBot")
async def help_cmd(inter: Interaction):
    desc = (
        "**Admin**\n"
        "• `/build` – Build roles/channels & post panels\n"
        "• `/repost_panels` – Repost verify/ticket buttons here\n"
        "• `/announce` – Send announcement embed\n\n"
        "**Everyone**\n"
        "• `/rules` – Show server rules\n"
        "• `/ping` – Check latency\n"
    )
    await inter.response.send_message(embed=blue_embed("ForgeBot Help", desc), ephemeral=True)


@tree.command(name="rules", description="Display server rules")
async def rules_cmd(inter: Interaction):
    rules = (
        "1) Be respectful. Hate speech or harassment = ban.\n"
        "2) No spam or scams.\n"
        "3) Use tickets for support/purchasing.\n"
        "4) Follow Discord ToS & Community Guidelines."
    )
    await inter.response.send_message(embed=blue_embed("Rules", rules), ephemeral=True)


def admin_check(inter: Interaction) -> bool:
    if not inter.guild or not isinstance(inter.user, discord.Member):
        return False
    return inter.user.guild_permissions.administrator or ADMIN_ROLE in {r.name for r in inter.user.roles}


@tree.command(name="announce", description="Send an announcement (Admin only)")
@app_commands.describe(message="The announcement text")
async def announce_cmd(inter: Interaction, message: str):
    if not admin_check(inter):
        return await inter.response.send_message("Admin only.", ephemeral=True)
    await inter.response.send_message(embed=blue_embed("Announcement", message))


@tree.command(name="repost_panels", description="Repost verify & ticket panels here (Admin only)")
async def repost_panels_cmd(inter: Interaction):
    if not admin_check(inter):
        return await inter.response.send_message("Admin only.", ephemeral=True)

    await inter.response.send_message("Posting panels…", ephemeral=True)
    await post_verify_panel(inter.channel)
    await post_ticket_panel(inter.channel)


@tree.command(name="build", description="Create roles/channels & post panels (Admin only)")
async def build_cmd(inter: Interaction):
    if not admin_check(inter):
        return await inter.response.send_message("Admin only.", ephemeral=True)

    await inter.response.send_message("Building server layout… this takes ~5s.", ephemeral=True)
    await run_builder(inter.guild)
    await inter.followup.send("Build complete. ✅", ephemeral=True)


# ------------------------------
# Main
# ------------------------------
def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Missing DISCORD_BOT_TOKEN environment variable. Put it in a .env file or Railway variable.")
    bot.run(token)


if __name__ == "__main__":
    main()

 ForgeBot Auto‑Builder (Fixed VerifyView) — Verify + Ticket System Only
# This patch removes the extra @ui.button decorator that caused a crash.

import os
import asyncio
import datetime as dt
from typing import Optional, Dict
import discord
from discord import app_commands, ui, ButtonStyle, Interaction, Embed, Permissions, Colour
from discord.ext import commands

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

THEME_COLOR = Colour.dark_blue()
CHECK_EMOJI = "✅"
TICKET_EMOJI = "🎫"
VERIFY_ROLE_NAME = "Verified"
TICKET_SUPPORT_ROLE = "Ticket Support"
ADMIN_ROLE = "admin"
OWNER_ROLE = "Owner"
BOT_ROLE = "Bot"
MEMBER_ROLE = "Member"
CHAN_VERIFY_LOGS = "verify-logs"
CHAN_MOD_LOGS = "mod-logs"
CHAN_TICKET_TRANSCRIPTS = "ticket-transcripts"
CAT_SUPPORT_TICKETS = "Support Tickets"
CHAN_CLOSED_TICKETS = "Closed Tickets"

def blue_embed(title: str, description: str = ""):
    e = Embed(title=title, description=description, color=THEME_COLOR)
    e.timestamp = dt.datetime.utcnow()
    return e

class VerifyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = ui.Button(
            label="Verify",
            emoji=CHECK_EMOJI,
            style=ButtonStyle.success,
            custom_id="forge_verify_btn"
        )
        self.add_item(button)

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = ui.Button(
            label="Create Ticket",
            emoji=TICKET_EMOJI,
            style=ButtonStyle.primary,
            custom_id="forge_ticket_btn"
        )
        self.add_item(button)

class CloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = ui.Button(
            label="Close Ticket",
            emoji="🔒",
            style=ButtonStyle.danger,
            custom_id="forge_close_btn"
        )
        self.add_item(button)

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseView())
    try:
        await tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Sync error:", e)
    print(f"Logged in as {bot.user}")

@bot.event
async def on_interaction(inter: Interaction):
    if not inter.type == discord.InteractionType.component:
        return
    cid = inter.data.get("custom_id")
    if cid == "forge_verify_btn":
        guild = inter.guild
        role = discord.utils.get(guild.roles, name=VERIFY_ROLE_NAME)
        if not role:
            role = await guild.create_role(name=VERIFY_ROLE_NAME, colour=THEME_COLOR)
        member = inter.user
        if role in member.roles:
            return await inter.response.send_message("Already verified ✅", ephemeral=True)
        await member.add_roles(role)
        await inter.response.send_message("You are now verified!", ephemeral=True)
        log = discord.utils.get(guild.text_channels, name=CHAN_VERIFY_LOGS)
        if log:
            await log.send(embed=blue_embed("User Verified", f"{member.mention} verified."))
    elif cid == "forge_ticket_btn":
        guild = inter.guild
        user = inter.user
        parent = discord.utils.get(guild.categories, name=CAT_SUPPORT_TICKETS)
        if parent is None:
            parent = await guild.create_category(CAT_SUPPORT_TICKETS)
        base = f"ticket-{user.name}".replace(" ", "-").lower()
        name = base
        i = 1
        while discord.utils.get(parent.text_channels, name=name):
            i += 1
            name = f"{base}-{i}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        ch = await guild.create_text_channel(name, category=parent, overwrites=overwrites)
        await ch.send(content=user.mention, embed=blue_embed("Ticket Created", "Staff will help soon."), view=CloseView())
        await inter.response.send_message(f"Created {ch.mention}", ephemeral=True)
    elif cid == "forge_close_btn":
        guild = inter.guild
        ch = inter.channel
        await inter.response.send_message("Closing ticket...", ephemeral=True)
        archive = discord.utils.get(guild.categories, name=CHAN_CLOSED_TICKETS)
        if not archive:
            archive = await guild.create_category(CHAN_CLOSED_TICKETS)
        await ch.edit(category=archive)

@tree.command(name="ping", description="Check bot latency")
async def ping(inter: Interaction):
    await inter.response.send_message(f"Pong! {round(bot.latency*1000)}ms", ephemeral=True)

def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Missing DISCORD_BOT_TOKEN variable")
    bot.run(token)

if __name__ == "__main__":
    main()

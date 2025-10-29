
# ForgeBot Premium – Safe Edition (Midnight-Blue)
Public-server-safe management bot with embeds, moderation, verification, tickets, admin tools, and fun commands.

## Features
- **Embeds**: `/embed preview|send|template_*` (midnight-blue theme)
- **General**: `/ping`, `/help`, `/invite`, `/about`
- **Moderation**: `/clear`, `/timeout`, `/kick`, `/ban`, `/warn`, `/warnings`
- **Verification**: `/verify_panel` assigns VERIFY_ROLE_ID on click
- **Tickets**: `/ticket_panel` opens private channel, has close button
- **Utility**: `/avatar`, `/userinfo`, `/serverinfo`, `/roleinfo`, `/say`
- **Fun**: `/8ball`, `/coinflip`, `/roll`
- **Admin**: `/announce`, `/slowmode`, `/lock`, `/unlock`

## Setup
1. Create a bot in the Developer Portal, invite with:
   - `applications.commands`, `Send Messages`, `Embed Links`, `Manage Channels`, `Manage Roles`, `Read Message History`
2. Install & run:
```bash
pip install -r requirements.txt
cp .env.example .env  # fill values
python bot.py
```
3. `.env`
```
DISCORD_BOT_TOKEN=YOUR_TOKEN
# Optional fast sync for a test guild:
# GUILD_ID=123456789012345678
# Roles & category
VERIFY_ROLE_ID=0
STAFF_ROLE_ID=0
TICKETS_CATEGORY_ID=0
```

## Notes
- Bot role must be **above** roles it manages.
- Tickets: set a category ID or leave blank to create at server root.
- Change embed theme in `cogs/embed_cog.py` (BRAND/parse_color/make_embed).

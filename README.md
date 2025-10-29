
# ForgeBot – Premium (No Stocks)
Slash-command bot with moderation, embeds, verification, and tickets.

## Features
- **Embeds**: `/embed preview`, `/embed send`, `/embed template_*`
- **Moderation**: `/purge`, `/timeout`, `/kick`, `/ban`
- **Utility**: `/ping`, `/serverinfo`, `/avatar`, `/say`
- **Verify**: `/verify_panel` → button assigns VERIFY_ROLE_ID
- **Tickets**: `/ticket_panel` → button opens private channel, includes close button

## Setup
1. **Create bot & invite** with these perms:
   - `applications.commands`, `Send Messages`, `Embed Links`, `Manage Channels`, `Manage Roles`, `Read Message History`
2. **Install**
```bash
pip install -r requirements.txt
cp .env.example .env   # fill values
python bot.py
```
3. **.env**
```
DISCORD_BOT_TOKEN=YOUR_TOKEN
# Optional faster sync to test guild:
# GUILD_ID=123456789012345678

# Verification (required for /verify_panel)
VERIFY_ROLE_ID=0

# Tickets (optional but recommended)
STAFF_ROLE_ID=0
TICKETS_CATEGORY_ID=0
```
Set the IDs from Discord (right-click → Copy ID with Developer Mode on).

## Commands
- Post verify panel in your verify channel:
  `/verify_panel title:"Verify" description:"Press to unlock channels"`
- Post ticket panel in a support channel:
  `/ticket_panel title:"Support" description:"Create a private ticket"`

## Notes
- The bot role must be **above** the roles it assigns/timeouts.
- For Railway: just set the same environment variables in **Variables** and run `python bot.py`.

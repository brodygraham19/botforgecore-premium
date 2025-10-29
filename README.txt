
ForgeBot Ultimate (Public-Safe)
===============================

Features
- Slash commands for moderation, utility, fun, and embeds
- Ticket button system (creates private channel + close button)
- Verification button system (assigns a role)
- Midnight-blue embeds
- Works on Railway/Replit/Local

Environment Variables (Railway/Render/Replit)
- DISCORD_BOT_TOKEN = your bot token
- GUILD_ID = optional: a single guild ID for faster command sync
- OWNER_ID = optional: your Discord user ID (for owner-only commands later)

Run locally
-----------
python -m venv venv
venv\Scripts\activate  (or source venv/bin/activate)
pip install -r requirements.txt
python bot.py

Post the buttons
----------------
1) Run the bot and in your server use:
   /post_verify role:@Verified
   /post_ticket staff_role:@Staff category:# (optional pick a Category)

Embed commands
--------------
/embed_send title: text description: text [color: pick] [thumbnail: url] [image: url] [footer: text] [mention_everyone: false]
/embed_template

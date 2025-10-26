# ForgeBot Ultimate (BotForge)
All-in-one Discord bot for your BotForge server: verification, tickets, shop, branding, utilities, and moderation.

## Quick Start (Railway)
1. Create a new Railway project from this repo/zip.
2. Add environment variable: `DISCORD_BOT_TOKEN` (keep your current token).
3. Deploy. Railway will run `python bot.py` via the `Procfile`.

## Local Run (Windows / macOS / Linux)
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Put your token in .env (copy .env.example -> .env and paste it)
python bot.py
```

### First Commands
- `/setup` -> auto-creates roles & channels (orders, support, logs, showcase).
- `/about`, `/theme`, `/logo` -> branding.
- `/verify` `/ticket open` `/ticket close`
- `/listbots` `/price` `/order` -> opens a ticket for orders.
- `/moderation` tools -> `/ban` `/mute` `/purge` etc.

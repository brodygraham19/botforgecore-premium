# ForgeBot (Public-Safe All-in-One)

**Features**
- Welcome messages to #welcome + DM
- Verify panel (button) -> grants Verified role, removes Unverified (optional)
- Ticket panel (button) -> creates private ticket channel visible to opener + Support Team
- Rich embed builder: `/embed create` (preview) and `/embed send` (send to a channel)
- Moderation: `/ban`, `/kick`, `/timeout`, `/mute` (role), `/purge`
- Utilities: `/avatar`, `/server`, `/user`, `/ping`
- AutoMod: simple link + profanity filter; auto-timeout configurable
- Giveaways: `/giveaway start` with join button + winner picker

**Run locally**
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill in IDs + token
python bot.py
```
**Railway**
- Add `DISCORD_BOT_TOKEN` (required) and any optional IDs as variables.
- Start command: `python bot.py`

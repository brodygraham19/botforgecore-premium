# ForgeBot Premium (Verify + Tickets)

## Files
- `ForgeBot.py` – main entry
- `cogs/verify.py` – verify button + /setup-verify
- `cogs/ticket.py` – ticket system + /setup-tickets
- `requirements.txt`

## Env Vars (Railway)
- DISCORD_BOT_TOKEN
- GUILD_ID
- VERIFY_ROLE_ID
- STAFF_ROLE_ID
- TICKET_CATEGORY_ID
- SUPPORT_LOG_CHANNEL_ID (optional)

## Start Command
```
python ForgeBot.py
```

## First-time Setup
1. Deploy with env vars.
2. In Discord, run `/setup-verify` where you want the verify button.
3. Run `/setup-tickets` in your tickets channel.

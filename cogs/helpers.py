from __future__ import annotations
import re
import discord
from typing import Optional

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")

def parse_color(value: Optional[str], default: int=0x0f172a) -> discord.Color:
    """Parse a hex string like '#1e90ff' into discord.Color; fallback to midnight-blue default."""
    if not value:
        return discord.Color(default)
    m = HEX_RE.match(value.strip())
    if not m:
        return discord.Color(default)
    return discord.Color(int(m.group(1), 16))

def get_role(guild: discord.Guild, role_id: int=0, fallback_name: str="") -> Optional[discord.Role]:
    if role_id:
        r = guild.get_role(role_id)
        if r:
            return r
    if fallback_name:
        for r in guild.roles:
            if r.name.lower() == fallback_name.lower():
                return r
    return None

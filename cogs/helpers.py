from __future__ import annotations
import re, discord
from typing import Optional

HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")

def parse_color(hex_str: str | None, default: int=0x0f172a) -> discord.Colour:
    if not hex_str: return discord.Colour(default)
    m = HEX_RE.match(hex_str.strip())
    if not m: return discord.Colour(default)
    return discord.Colour(int(m.group(1), 16))

def get_role(guild: discord.Guild, role_id: int=0, fallback_name: str="") -> Optional[discord.Role]:
    if role_id:
        r = guild.get_role(role_id)
        if r: return r
    if fallback_name:
        for r in guild.roles:
            if r.name.lower() == fallback_name.lower():
                return r
    return None


# cogs/embed_cog.py
from __future__ import annotations
import re, json, pathlib
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

HEX_RE = re.compile(r"^#?(?:[0-9a-fA-F]{6})$")
BRAND = {
    "midnight_blue": 0x0B1220,
    "forge_blue": 0x0EA5E9,
    "success_green": 0x22C55E,
    "warning_yellow": 0xEAB308,
    "danger_red": 0xEF4444,
    "grey": 0x6B7280,
}

def parse_color(v: Optional[str]) -> discord.Color:
    if not v:
        return discord.Color(BRAND["midnight_blue"])
    k = v.strip().lower().replace(" ", "_")
    if k in BRAND:
        return discord.Color(BRAND[k])
    if HEX_RE.match(k):
        if not k.startswith("#"): k = "#" + k
        return discord.Color(int(k[1:], 16))
    raise ValueError("Invalid color. Use a named color (midnight_blue) or HEX like #0ea5e9.")

def url_ok(u: Optional[str]) -> bool:
    return bool(u and (u.startswith("http://") or u.startswith("https://")))

def make_embed(
    title: Optional[str], description: Optional[str], color: Optional[str],
    image_url: Optional[str], thumbnail_url: Optional[str],
    footer: Optional[str], author_name: Optional[str], author_icon: Optional[str],
) -> discord.Embed:
    emb = discord.Embed(title=title or "", description=description or "", color=parse_color(color))
    if image_url and url_ok(image_url): emb.set_image(url=image_url)
    if thumbnail_url and url_ok(thumbnail_url): emb.set_thumbnail(url=thumbnail_url)
    if author_name:
        if author_icon and url_ok(author_icon):
            emb.set_author(name=author_name, icon_url=author_icon)
        else:
            emb.set_author(name=author_name)
    emb.set_footer(text=footer or "BotForge • Premium")
    return emb

TEMPLATES_DIR = pathlib.Path("./templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

def _safe(name: str) -> str:
    import re as _re
    return _re.sub(r"[^a-zA-Z0-9_\- ]", "", name).strip().replace(" ", "_")

def _path(name: str) -> pathlib.Path:
    return TEMPLATES_DIR / f"{_safe(name)}.json"

class EmbedGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="embed", description="Create and manage custom embeds.")

    @app_commands.command(name="preview", description="Preview a custom embed (ephemeral).")
    async def preview(self, interaction: discord.Interaction,
                      title: Optional[str]=None,
                      description: Optional[str]=None,
                      color: Optional[str]=None,
                      image_url: Optional[str]=None,
                      thumbnail_url: Optional[str]=None,
                      footer: Optional[str]=None,
                      author_name: Optional[str]=None,
                      author_icon: Optional[str]=None):
        try:
            emb = make_embed(title, description, color, image_url, thumbnail_url, footer, author_name, author_icon)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True); return
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name="send", description="Send a custom embed to a channel.")
    async def send(self, interaction: discord.Interaction,
                   channel: Optional[discord.TextChannel]=None,
                   title: Optional[str]=None,
                   description: Optional[str]=None,
                   color: Optional[str]=None,
                   image_url: Optional[str]=None,
                   thumbnail_url: Optional[str]=None,
                   footer: Optional[str]=None,
                   ping_role: Optional[discord.Role]=None,
                   author_name: Optional[str]=None,
                   author_icon: Optional[str]=None,
                   suppress_links: Optional[bool]=False):
        try:
            emb = make_embed(title, description, color, image_url, thumbnail_url, footer, author_name, author_icon)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True); return
        target = channel or interaction.channel
        content = ping_role.mention if ping_role else None
        await target.send(content=content, embed=emb, suppress=suppress_links or False)
        await interaction.response.send_message(f"✅ Sent to {target.mention}", ephemeral=True)

    @app_commands.command(name="template_save", description="Save a template by name.")
    async def template_save(self, interaction: discord.Interaction, name: str,
                            title: Optional[str]=None, description: Optional[str]=None,
                            color: Optional[str]=None, image_url: Optional[str]=None,
                            thumbnail_url: Optional[str]=None, footer: Optional[str]=None,
                            author_name: Optional[str]=None, author_icon: Optional[str]=None):
        data = {"title":title,"description":description,"color":color,
                "image_url":image_url,"thumbnail_url":thumbnail_url,"footer":footer,
                "author_name":author_name,"author_icon":author_icon}
        _path(name).write_text(json.dumps(data, indent=2), encoding="utf-8")
        await interaction.response.send_message(f"💾 Saved template **{name}**.", ephemeral=True)

    @app_commands.command(name="template_load", description="Load a template and send it.")
    async def template_load(self, interaction: discord.Interaction, name: str,
                            channel: Optional[discord.TextChannel]=None,
                            ping_role: Optional[discord.Role]=None,
                            suppress_links: Optional[bool]=False):
        p = _path(name)
        if not p.exists():
            await interaction.response.send_message("❌ Template not found.", ephemeral=True); return
        data = json.loads(p.read_text(encoding="utf-8"))
        try:
            emb = make_embed(**data)
        except ValueError as e:
            await interaction.response.send_message(f"❌ {e}", ephemeral=True); return
        target = channel or interaction.channel
        content = ping_role.mention if ping_role else None
        await target.send(content=content, embed=emb, suppress=suppress_links or False)
        await interaction.response.send_message(f"✅ Template **{name}** sent to {target.mention}.", ephemeral=True)

    @app_commands.command(name="template_list", description="List saved templates.")
    async def template_list(self, interaction: discord.Interaction):
        items = [p.stem for p in TEMPLATES_DIR.glob("*.json")]
        if not items:
            await interaction.response.send_message("No templates saved.", ephemeral=True); return
        await interaction.response.send_message("📚 Templates:\n- " + "\n- ".join(items), ephemeral=True)

    @app_commands.command(name="template_delete", description="Delete a template.")
    async def template_delete(self, interaction: discord.Interaction, name: str):
        p = _path(name)
        if p.exists():
            p.unlink()
            await interaction.response.send_message(f"🗑️ Deleted **{name}**.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Template not found.", ephemeral=True)

class EmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.add_command(EmbedGroup())

async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedCog(bot))

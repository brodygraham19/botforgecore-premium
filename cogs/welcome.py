from __future__ import annotations
import os
import discord
from discord.ext import commands
from discord import app_commands
from .helpers import get_role, parse_color

MIDNIGHT = 0x0f172a

class VerifyView(discord.ui.View):
    def __init__(self, verified_role_id: int=0, unverified_role_id: int=0, timeout: float=None):
        super().__init__(timeout=timeout)
        self.verified_role_id = verified_role_id
        self.unverified_role_id = unverified_role_id

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="forge:verify")
    async def verify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        if guild is None:
            return await interaction.response.send_message("This button only works in a server.", ephemeral=True)

        verified = get_role(guild, self.verified_role_id, "Verified")
        if verified is None:
            return await interaction.response.send_message("Verified role not set/found. Admin: set VERIFIED_ROLE_ID or create a 'Verified' role.", ephemeral=True)

        try:
            await user.add_roles(verified, reason="ForgeBot verify button")
            if self.unverified_role_id:
                unv = guild.get_role(self.unverified_role_id)
                if unv:
                    await user.remove_roles(unv, reason="ForgeBot verify button")
            await interaction.response.send_message(f"You're verified, {user.mention}! 🎉", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to manage roles. Move my role above the Verified role.", ephemeral=True)

class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_channel_id = int(os.getenv("WELCOME_CHANNEL_ID", "0"))
        self.verified_role_id = int(os.getenv("VERIFIED_ROLE_ID", "0"))
        self.unverified_role_id = int(os.getenv("UNVERIFIED_ROLE_ID", "0"))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Post in #welcome channel
        channel = None
        if self.welcome_channel_id:
            channel = member.guild.get_channel(self.welcome_channel_id)
        if channel is None:
            # try lookup by name
            for ch in member.guild.text_channels:
                if ch.name.lower() == "welcome":
                    channel = ch
                    break
        emb = discord.Embed(
            title="Welcome to the server!",
            description=f"{member.mention}, we're glad you're here. Please read the rules and press **Verify** to unlock channels.",
            color=discord.Color(MIDNIGHT)
        )
        emb.set_thumbnail(url=getattr(member.avatar, 'url', discord.Embed.Empty))
        if channel:
            try:
                await channel.send(embed=emb, view=VerifyView(self.verified_role_id, self.unverified_role_id))
            except Exception:
                pass
        # DM the member
        try:
            await member.send(embed=emb)
        except Exception:
            pass

    @app_commands.command(name="rules_panel", description="Post the rules + verify button panel here")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def rules_panel(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Server Rules & Verification",
            description=(
                "1) Be respectful • 2) No hate or harassment • 3) No NSFW • 4) No spam/scam

"
                "Press **Verify** to accept the rules and unlock the server."
            ),
            color=discord.Color(MIDNIGHT)
        )
        await interaction.response.send_message(embed=emb, view=VerifyView(self.verified_role_id, self.unverified_role_id))

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))

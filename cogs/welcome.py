from __future__ import annotations
import os, discord
from discord.ext import commands
from discord import app_commands
from .helpers import get_role

MIDNIGHT = 0x0f172a

class VerifyView(discord.ui.View):
    def __init__(self, verified_role_id: int=0, unverified_role_id: int=0):
        super().__init__(timeout=None)
        self.verified_role_id = verified_role_id
        self.unverified_role_id = unverified_role_id

    @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="forge:verify")
    async def verify_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("This only works in a server.", ephemeral=True)
        role = get_role(guild, self.verified_role_id, "Verified")
        if role is None:
            return await interaction.response.send_message("Verified role not found. Create a role named 'Verified' or set VERIFIED_ROLE_ID.", ephemeral=True)
        try:
            await interaction.user.add_roles(role, reason="ForgeBot verification")
            if self.unverified_role_id:
                ur = guild.get_role(self.unverified_role_id)
                if ur: await interaction.user.remove_roles(ur, reason="ForgeBot verification")
            await interaction.response.send_message("You're verified! 🎉", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I need Manage Roles and to be above the role.", ephemeral=True)

class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_channel_id = int(os.getenv("WELCOME_CHANNEL_ID","0"))
        self.verified_role_id = int(os.getenv("VERIFIED_ROLE_ID","0"))
        self.unverified_role_id = int(os.getenv("UNVERIFIED_ROLE_ID","0"))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch = None
        if self.welcome_channel_id:
            ch = member.guild.get_channel(self.welcome_channel_id)
        if ch is None:
            for c in member.guild.text_channels:
                if c.name.lower() == "welcome":
                    ch = c; break
        emb = discord.Embed(
            title="Welcome to the server!",
            description=f"{member.mention}, please read the rules and press **Verify** to unlock channels.",
            colour=discord.Colour(MIDNIGHT)
        )
        if ch:
            try: await ch.send(embed=emb, view=VerifyView(self.verified_role_id, self.unverified_role_id))
            except Exception: pass
        try: await member.send(embed=emb)
        except Exception: pass

    @app_commands.command(name="rules_panel", description="Post the rules and verify button")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def rules_panel(self, interaction: discord.Interaction):
        emb = discord.Embed(
            title="Rules & Verification",
            description=(
                "1) Be respectful\n"
                "2) No hate/harassment\n"
                "3) No NSFW or spam\n"
                "4) Follow Discord TOS\n\n"
                "Press **Verify** to accept and unlock the server."
            ),
            colour=discord.Colour(MIDNIGHT)
        )
        await interaction.response.send_message(embed=emb, view=VerifyView(self.verified_role_id, self.unverified_role_id))

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))

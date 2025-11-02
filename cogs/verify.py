
import discord, os
from discord.ext import commands
from discord import app_commands

VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
VERIFY_LOGS_CHANNEL_ID = os.getenv("VERIFY_LOGS_CHANNEL_ID")

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Verify", style=discord.ButtonStyle.success, custom_id="verify_btn"))

class Verify(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def setup_persistent_views(self): self.bot.add_view(VerifyView())

    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        try:
            if VERIFY_LOGS_CHANNEL_ID and VERIFY_LOGS_CHANNEL_ID.isdigit():
                ch = guild.get_channel(int(VERIFY_LOGS_CHANNEL_ID))
                if ch: await ch.send(embed=embed)
        except Exception: pass

    @app_commands.command(name="verifypanel", description="Send verification panel")
    async def verifypanel(self, interaction: discord.Interaction):
        em = discord.Embed(title="✅ Verification", description="Click the button to verify yourself.", color=0x2b2d31)
        await interaction.response.send_message("✅ Panel sent", ephemeral=True)
        await interaction.channel.send(embed=em, view=VerifyView())

    @app_commands.command(name="verify", description="Verify a user (admin)")
    async def verify_user(self, interaction: discord.Interaction, user: discord.Member):
        role = interaction.guild.get_role(int(VERIFY_ROLE_ID)) if VERIFY_ROLE_ID and VERIFY_ROLE_ID.isdigit() else None
        if not role:
            return await interaction.response.send_message("❌ Verify role not configured.", ephemeral=True)
        await user.add_roles(role, reason=f"Manual verify by {interaction.user}")
        await interaction.response.send_message(f"✅ {user.mention} verified.")
        await self._log(interaction.guild, discord.Embed(description=f"✅ **Verified:** {user.mention}", color=0x57F287))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "verify_btn":
            role = interaction.guild.get_role(int(VERIFY_ROLE_ID)) if VERIFY_ROLE_ID and VERIFY_ROLE_ID.isdigit() else None
            if not role:
                return await interaction.response.send_message("❌ Verify role not set.", ephemeral=True)
            await interaction.user.add_roles(role, reason="Self verify")
            await interaction.response.send_message("✅ You are verified!", ephemeral=True)
            await self._log(interaction.guild, discord.Embed(description=f"✅ **Self-verified:** {interaction.user.mention}", color=0x57F287))

async def setup(bot):
    await bot.add_cog(Verify(bot))

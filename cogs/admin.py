
import os
import discord
from discord import app_commands
from discord.ext import commands

MIDNIGHT = 0x0a192f

def admin_only():
    return app_commands.checks.has_permissions(manage_guild=True)

class ButtonViews:
    class VerifyView(discord.ui.View):
        def __init__(self, verified_role_id: int, timeout: float | None = None):
            super().__init__(timeout=timeout)
            self.verified_role_id = verified_role_id

        @discord.ui.button(label="✅ Verify", style=discord.ButtonStyle.success, custom_id="forge:verify")
        async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
            role = interaction.guild.get_role(self.verified_role_id)
            if not role:
                await interaction.response.send_message("Verification role missing.", ephemeral=True)
                return
            try:
                await interaction.user.add_roles(role, reason="Verified via button")
                await interaction.response.send_message("You are verified! 🎉", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I lack permission to add the role.", ephemeral=True)

    class TicketOpenView(discord.ui.View):
        def __init__(self, staff_role_id: int, category_id: int | None = None):
            super().__init__(timeout=None)
            self.staff_role_id = staff_role_id
            self.category_id = category_id

        @discord.ui.button(label="🎫 Open Ticket", style=discord.ButtonStyle.primary, custom_id="forge:open_ticket")
        async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
            guild = interaction.guild
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            }
            staff_role = guild.get_role(self.staff_role_id)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
            category = guild.get_channel(self.category_id) if self.category_id else None

            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.name}".lower()[:90],
                overwrites=overwrites,
                category=category
            )
            view = ButtonViews.TicketCloseView()
            e = discord.Embed(title="Support Ticket Opened", description="A staff member will be with you shortly.\nUse the button below to close when finished.", color=MIDNIGHT)
            await channel.send(content=staff_role.mention if staff_role else None, embed=e, view=view)
            await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)

    class TicketCloseView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="forge:close_ticket")
        async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("Closing in 5 seconds…", ephemeral=True)
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
            try:
                await interaction.channel.delete(reason="Ticket closed")
            except discord.Forbidden:
                await interaction.followup.send("I lack permission to delete this channel.", ephemeral=True)

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="post_verify", description="Post a Verify button embed in this channel")
    @app_commands.describe(role="Role to assign when users verify")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def post_verify(self, interaction: discord.Interaction, role: discord.Role):
        e = discord.Embed(title="Verification", description="Click the button to verify and gain access.", color=MIDNIGHT)
        view = ButtonViews.VerifyView(verified_role_id=role.id)
        await interaction.response.send_message(embed=e, view=view)

    @app_commands.command(name="post_ticket", description="Post a Ticket button in this channel")
    @app_commands.describe(staff_role="Staff role pinged & allowed to view tickets", category="Optional category to create tickets under")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def post_ticket(self, interaction: discord.Interaction, staff_role: discord.Role, category: discord.CategoryChannel | None = None):
        e = discord.Embed(title="Need Help?", description="Press the button to open a private ticket with staff.", color=MIDNIGHT)
        view = ButtonViews.TicketOpenView(staff_role_id=staff_role.id, category_id=category.id if category else None)
        await interaction.response.send_message(embed=e, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))

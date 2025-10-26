import discord
from discord.ext import commands
from discord.ui import View, Button
import os

# ---- Setup ----
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---- Verify View ----
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            Button(label="✅ Verify",
                   style=discord.ButtonStyle.green,
                   custom_id="verify_button")
        )

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced ({len(synced)})")
    except Exception as e:
        print(f"❌ Sync error: {e}")

# ---- Verify Button ----
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data and interaction.data.get("custom_id") == "verify_button":
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                "✅ You are now verified!", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "⚠️ 'Verified' role not found.", ephemeral=True
            )

# ---- Ticket Setup ----
@bot.tree.command(name="ticketsetup", description="Create a ticket panel (Admin only)")
async def ticketsetup(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ You need admin permissions.", ephemeral=True
        )

    embed = discord.Embed(
        title="🎟 Support Tickets",
        description="Click below to create a support ticket.",
        color=discord.Color.blurple()
    )
    view = View()
    view.add_item(
        Button(label="🎫 Create Ticket",
               style=discord.ButtonStyle.blurple,
               custom_id="create_ticket")
    )
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message(
        "✅ Ticket system created.", ephemeral=True
    )

# ---- Ticket Create ----
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data and interaction.data.get("custom_id") == "create_ticket":
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
        }
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            reason="New Support Ticket",
        )
        await interaction.response.send_message(
            f"🎟 Ticket created: {channel.mention}", ephemeral=True
        )

# ---- Run Bot ----
bot.run(os.getenv("DISCORD_BOT_TOKEN"))

import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} commands successfully.")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

@bot.tree.command(name="help", description="Show list of available commands.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 BotForgeCore Premium Commands",
        description=(
            "**/help** - Show this menu\n"
            "**/ping** - Check if the bot is online\n"
            "**/rules** - Display the server rules\n"
            "**/verify** - Verify yourself to access the server\n"
            "**/ticketsetup** - Create the ticket panel (Admin only)\n"
            "**/announce** - Send a server announcement (Admin only)\n"
            "**/clear** - Clear messages (Admin only)\n"
            "**/ban**, **/kick**, **/unban** - Moderate members\n"
            "**/sync** - Force sync commands (Admin only)"
        ),
        color=discord.Color.blurple()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot is online.")

@bot.tree.command(name="rules", description="Display server rules.")
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 Server Rules",
        description=(
            "1️⃣ Be respectful to everyone.\n"
            "2️⃣ No spamming or harassment.\n"
            "3️⃣ Keep topics in the right channels.\n"
            "4️⃣ Follow Discord ToS.\n"
            "5️⃣ Have fun!"
        ),
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="verify", description="Verify yourself to access the server.")
async def verify(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name="Verified")
    if role is None:
        await interaction.response.send_message("⚠️ No 'Verified' role found.", ephemeral=True)
        return

    await interaction.user.add_roles(role)
    await interaction.response.send_message("✅ You’ve been verified!", ephemeral=True)

@bot.tree.command(name="announce", description="Send an announcement (Admin only).")
@app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, title: str, message: str):
    embed = discord.Embed(title=title, description=message, color=discord.Color.gold())
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("📢 Announcement sent.", ephemeral=True)

@bot.tree.command(name="clear", description="Clear chat messages (Admin only).")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Cleared {amount} messages.", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a member (Admin only).")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} has been kicked. Reason: {reason}")

@bot.tree.command(name="ban", description="Ban a member (Admin only).")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"🔨 {member} has been banned. Reason: {reason}")

@bot.tree.command(name="unban", description="Unban a user (Admin only).")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, username: str):
    banned_users = await interaction.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == username:
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ Unbanned {user.name}")
            return
    await interaction.response.send_message("⚠️ User not found.")

@bot.tree.command(name="ticketsetup", description="Set up the ticket system (Admin only).")
@app_commands.checks.has_permissions(administrator=True)
async def ticketsetup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Click the button below to create a support ticket.",
        color=discord.Color.green()
    )
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="🎟️ Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket"))
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "create_ticket":
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")
        channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category)
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await channel.send(f"{interaction.user.mention}, a staff member will assist you soon.")
        await interaction.response.send_message("✅ Your ticket has been created!", ephemeral=True)

@bot.tree.command(name="sync", description="Manually sync slash commands (Admin only).")
@app_commands.checks.has_permissions(administrator=True)
async def sync_commands(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    try:
        synced = await bot.tree.sync()
        await interaction.followup.send(f"✅ Synced {len(synced)} commands successfully.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error syncing: `{e}`")

bot.run(DISCORD_TOKEN)

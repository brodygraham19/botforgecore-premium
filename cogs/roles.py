
import discord
from discord.ext import commands
from discord import app_commands

class RoleButton(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.role_id = role_id
        self.add_item(discord.ui.Button(label="Get Role", style=discord.ButtonStyle.secondary, custom_id=f"rolebtn:{role_id}"))

class Roles(commands.Cog):
    def __init__(self, bot): self.bot = bot

    async def setup_persistent_views(self):
        pass  # dynamic

    @app_commands.command(name="rolebutton", description="Create a role button panel for a role ID")
    async def rolebutton(self, interaction: discord.Interaction, role_id: str, label: str = "Get Role"):
        if not role_id.isdigit():
            return await interaction.response.send_message("❌ Provide a numeric role ID.", ephemeral=True)
        view = RoleButton(int(role_id))
        # adjust label
        view.children[0].label = label
        embed = discord.Embed(title="Role Button", description=f"Click to toggle <@&{role_id}>", color=0x2b2d31)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Role button created.", ephemeral=True)

    @commands.Cog.listener()
    async def on_interaction(self, i: discord.Interaction):
        if i.type != discord.InteractionType.component: return
        cid = i.data.get("custom_id", "")
        if cid.startswith("rolebtn:"):
            role_id = int(cid.split(":")[1])
            role = i.guild.get_role(role_id)
            if not role:
                return await i.response.send_message("Role missing.", ephemeral=True)
            if role in i.user.roles:
                await i.user.remove_roles(role)
                await i.response.send_message(f"❎ Removed {role.mention}", ephemeral=True)
            else:
                await i.user.add_roles(role)
                await i.response.send_message(f"✅ Added {role.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Roles(bot))

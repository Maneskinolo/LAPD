import discord
from discord.ext import commands
from discord import app_commands, ButtonStyle, Interaction
from datetime import datetime

# Role and Channel IDs
PERMS_ROLE_ID = 1376656549623234611# Role ID for permission to use !warrant
PING_ROLE_ID = 1292541838904791040   # Role ID to ping when warrant is logged
LOG_CHANNEL_ID = 1377974406277501021  # Channel ID for unauthorized access logs
ALERT_ROLE_ID = 1337050305153470574  # Role to ping for unauthorized access

class WarrantModal(discord.ui.Modal, title="Log a Warrant"):
    def __init__(self):
        super().__init__()
        self.suspectusername = discord.ui.TextInput(
            label="Suspect Username",
            placeholder="Enter suspect(s) username(s)",
            required=True
        )
        self.physicaldescription = discord.ui.TextInput(
            label="Physical Description",
            placeholder="Enter suspect's physical description (ex. Brown hair)",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.crimes = discord.ui.TextInput(
            label="Crimes",
            placeholder="List the crimes that the suspect(s) have commited. (ex. Bank robbery)",
            required=True
        )
        self.dangerousitylevel = discord.ui.TextInput(
            label="Wanted Level (1-10)",
            placeholder="Enter the wanted level of the suspect(s) (ex. 5)",
            required=True
        )
        self.warrantid = discord.ui.TextInput(
            label="Warrant ID",
            placeholder="Enter warrant ID (ex. Warrant 04)",
            required=True
        )
        self.add_item(self.suspectusername)
        self.add_item(self.physicaldescription)
        self.add_item(self.crimes)
        self.add_item(self.dangerousitylevel)
        self.add_item(self.warrantid)

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(
            title="🚨 New Warrant 🚨",
            description="A new warrant has just been issued. Please send a picture of the suspect(s) if you have one.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Suspect Username", value=self.suspectusername.value, inline=False)
        embed.add_field(name="Physical Description", value=self.physicaldescription.value, inline=False)
        embed.add_field(name="Crimes", value=self.crimes.value, inline=False)
        embed.add_field(name="Wanted Level", value=self.dangerousitylevel.value, inline=False)
        embed.add_field(name="Warrant ID", value=self.warrantid.value, inline=False)
        ping_message = f"<@&{PING_ROLE_ID}>"
        await interaction.response.send_message(content=ping_message, embed=embed)

class WarrantButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Log a Warrant", style=ButtonStyle.red)
    async def warrant_button(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(WarrantModal())

class LAPD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="warrant")
    async def warrant(self, ctx: commands.Context):
        if PERMS_ROLE_ID not in [role.id for role in ctx.author.roles]:
            # Send unauthorized message to channel (not ephemeral)
            await ctx.send("Unauthorized access detected ⚠️ ! An alert has been sent to the bot tamer.")
            # Send embed to log channel
            log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="Attempted use of a restricted command",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="User", value=ctx.author.mention, inline=False)
                embed.add_field(name="Message", value=ctx.message.content or "No message content", inline=False)
                embed.add_field(
                    name="Jump to message",
                    value=f"[Click here]({ctx.message.jump_url})",
                    inline=False
                )
                ping_message = f"<@&{ALERT_ROLE_ID}>"
                await log_channel.send(content=ping_message, embed=embed)
            else:
                print(f"Error: Could not find log channel with ID {LOG_CHANNEL_ID}")
            return
        view = WarrantButton()
        await ctx.send("Click the button to log a warrant (restricted access):", view=view)

async def setup(bot):
    await bot.add_cog(LAPD(bot))

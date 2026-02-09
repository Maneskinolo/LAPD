import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
from discord import Interaction, TextStyle, File
from datetime import datetime
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# Simulated callsign storage (replace with real database later if needed)
callsigns_db = {}  # Format: {user_id: callsign}

# Constants
REQUIRED_ROLE_ID = 1292541838904791040
ALLOWED_ROLE_ID = 1339058176003407915
ALERT_CHANNEL_ID = 1377974406277501021
CALLSIGN_LIST_CHANNEL_ID = 1344921844557414411
CALLSIGN_REQUEST_CHANNEL_ID = 1353106180406509682

# ──────────────────────────────────────────────
# Callsign Modal
# ──────────────────────────────────────────────
class CallsignModal(discord.ui.Modal, title="Request a Callsign"):
    roblox_discord = TextInput(
        label="Roblox + Discord User",
        placeholder="Enter your Roblox and Discord username",
        required=True
    )
    callsign = TextInput(
        label="Callsign Requested",
        placeholder="Enter the callsign you want",
        required=True
    )

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(
            title="Callsign Request",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Who", value=interaction.user.mention, inline=False)
        embed.add_field(name="Callsign", value=self.callsign.value, inline=False)

        view = View(timeout=None)
        accept = Button(
            label="Accept",
            style=discord.ButtonStyle.green,
            custom_id=f"accept_callsign_{interaction.user.id}_{self.callsign.value.replace(' ', '_')}"
        )
        deny = Button(
            label="Deny",
            style=discord.ButtonStyle.red,
            custom_id=f"deny_callsign_{interaction.user.id}"
        )

        async def accept_cb(inter: Interaction):
            parts = inter.data['custom_id'].split('_')
            uid = int(parts[2])
            callsign = '_'.join(parts[3:]).replace('_', ' ')
            callsigns_db[uid] = callsign
            await inter.response.send_message(f"✅ Callsign `{callsign}` approved for <@{uid}>!", ephemeral=True)
            accept.disabled = True
            deny.disabled = True
            await inter.message.edit(view=view)

        async def deny_cb(inter: Interaction):
            uid = int(inter.data['custom_id'].split('_')[2])
            await inter.response.send_message(f"❌ Callsign request for <@{uid}> denied.", ephemeral=True)
            accept.disabled = True
            deny.disabled = True
            await inter.message.edit(view=view)

        accept.callback = accept_cb
        deny.callback = deny_cb
        view.add_item(accept)
        view.add_item(deny)

        channel = interaction.guild.get_channel(CALLSIGN_REQUEST_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message("Callsign request submitted!", ephemeral=True)
        else:
            await interaction.response.send_message("Error: Request channel not found.", ephemeral=True)


# ──────────────────────────────────────────────
# Arrest Modal
# ──────────────────────────────────────────────
class ArrestModal(discord.ui.Modal, title="Log an Arrest"):
    suspect = TextInput(label="Suspect", placeholder="Enter suspect(s) name", required=True)
    charges = TextInput(label="Charges", placeholder="List the charges", style=TextStyle.paragraph, required=True)
    primary_officer = TextInput(label="Primary Officer", placeholder="Enter primary officer name", required=True)
    other_officers = TextInput(label="Secondary and Tertiary Officers", placeholder="Names + callsign or N/A", required=False)
    notes = TextInput(label="Notes", placeholder="Additional notes (optional)", style=TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: Interaction):
        embed = discord.Embed(
            title="New Arrest Log",
            description="Please send the mugshot!",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Suspect", value=self.suspect.value, inline=False)
        embed.add_field(name="Crimes", value=self.charges.value, inline=False)
        embed.add_field(name="Primary Officer", value=self.primary_officer.value, inline=False)
        embed.add_field(name="Secondary and Tertiary Officers", value=self.other_officers.value or "None", inline=False)
        embed.add_field(name="Notes", value=self.notes.value or "None", inline=False)
        await interaction.response.send_message(embed=embed)


# ──────────────────────────────────────────────
# Incident Report Modal + PDF generation
# ──────────────────────────────────────────────
class IncidentModal(discord.ui.Modal, title="Incident Report"):
    incident = TextInput(
        label="Incident Description",
        placeholder="Describe what happened",
        style=TextStyle.paragraph,
        required=True
    )
    officers = TextInput(
        label="Officers Involved",
        placeholder="List officers (name + callsign)",
        style=TextStyle.paragraph,
        required=True
    )
    notes = TextInput(
        label="Additional Notes",
        placeholder="Any extra information (optional)",
        style=TextStyle.paragraph,
        required=False
    )

    async def on_submit(self, interaction: Interaction):
        # Create PDF in memory
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(1 * inch, height - 1 * inch, "LAPD Incident Report")

        pdf.setFont("Helvetica", 12)
        y = height - 1.8 * inch
        pdf.drawString(1 * inch, y, f"Submitted by: {interaction.user.display_name} ({interaction.user.id})")
        pdf.drawString(1 * inch, y - 20, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y -= 60
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(1 * inch, y, "Incident Description:")
        pdf.setFont("Helvetica", 11)
        y -= 20
        self._draw_wrapped_text(pdf, self.incident.value, 1 * inch, y, width - 2 * inch)
        y -= (len(self.incident.value.split('\n')) * 15) + 40

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(1 * inch, y, "Officers Involved:")
        pdf.setFont("Helvetica", 11)
        y -= 20
        self._draw_wrapped_text(pdf, self.officers.value, 1 * inch, y, width - 2 * inch)
        y -= (len(self.officers.value.split('\n')) * 15) + 40

        if self.notes.value:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(1 * inch, y, "Additional Notes:")
            pdf.setFont("Helvetica", 11)
            y -= 20
            self._draw_wrapped_text(pdf, self.notes.value, 1 * inch, y, width - 2 * inch)

        pdf.save()
        buffer.seek(0)

        filename = f"incident-report-{interaction.user.id}-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"

        # Create embed
        embed = discord.Embed(
            title="New Incident Report",
            description="Incident report has been submitted and attached as PDF.",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Incident", value=self.incident.value[:1024], inline=False)
        embed.add_field(name="Officers Involved", value=self.officers.value[:1024], inline=False)
        embed.add_field(name="Additional Notes", value=self.notes.value or "None", inline=False)
        embed.set_footer(text=f"Submitted by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        # Send embed + PDF attachment
        file = File(buffer, filename=filename)
        await interaction.response.send_message(embed=embed, file=file)


    def _draw_wrapped_text(self, pdf, text, x, y_start, max_width):
        """Helper to wrap long text in PDF"""
        lines = text.split('\n')
        y = y_start
        for line in lines:
            words = line.split()
            current_line = ""
            for word in words:
                test = current_line + word + " "
                if pdf.stringWidth(test) < max_width:
                    current_line = test
                else:
                    pdf.drawString(x, y, current_line.strip())
                    y -= 14
                    current_line = word + " "
            if current_line:
                pdf.drawString(x, y, current_line.strip())
                y -= 14
        return y


# ──────────────────────────────────────────────
# Panel Cog
# ──────────────────────────────────────────────
class Panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.required_role_id = REQUIRED_ROLE_ID
        self.punishment_roles = [
            1306382455044964415, 1306382453283225650,
            1306382451228016660, 1306382449378594867,
            1324540074834133033, 1324540189594353787
        ]
        bot.add_listener(self.on_member_update, "on_member_update")

    @commands.command()
    async def panel(self, ctx):
        embed = discord.Embed(
            title="Welcome to Your Panel",
            description="Use the buttons below to access features.",
            color=discord.Color.blue()
        )
        embed.add_field(name="📝 Log Arrest", value="Use this to log an arrest.", inline=False)
        embed.add_field(name="👮 View Punishments", value="See your active punishments.", inline=False)
        embed.add_field(name="📢 Request Callsign", value="Request a unit callsign.", inline=False)
        embed.add_field(name="🚨 Incident Report", value="Report incidents that happened on duty.", inline=False)
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/497/Los_Angeles_Police_Department_seal.svg/512px-Los_Angeles_Police_Department_seal.svg.png")

        view = View(timeout=None)

        log_btn = Button(label="Log Arrest", style=discord.ButtonStyle.primary, custom_id="log_arrest")
        log_btn.callback = lambda i: i.response.send_modal(ArrestModal())

        pun_btn = Button(label="View Punishments", style=discord.ButtonStyle.secondary, custom_id="view_punishments")
        async def pun_cb(inter):
            user_roles = [r.id for r in inter.user.roles]
            active = [f"<@&{r}>" for r in self.punishment_roles if r in user_roles]
            embed = discord.Embed(
                title=f"Punishments for - {inter.user.display_name} -",
                description="\n".join(active) if active else "No active punishments.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        pun_btn.callback = pun_cb

        call_btn = Button(label="Request Callsign", style=discord.ButtonStyle.green, custom_id="request_callsign")
        call_btn.callback = lambda i: i.response.send_modal(CallsignModal())

        incident_btn = Button(label="Incident Report", style=discord.ButtonStyle.blurple, custom_id="incident_report")
        incident_btn.callback = lambda i: i.response.send_modal(IncidentModal())

        view.add_item(log_btn)
        view.add_item(pun_btn)
        view.add_item(call_btn)
        view.add_item(incident_btn)

        await ctx.send(embed=embed, view=view)

    # ──────────────────────────────────────────────
    # Other commands (unchanged)
    # ──────────────────────────────────────────────

    @commands.command()
    async def callsigns(self, ctx):
        embed = discord.Embed(title="Callsigns", color=discord.Color.blue(), timestamp=datetime.now())
        if callsigns_db:
            embed.description = "\n".join([f"<@{uid}>: {cs}" for uid, cs in callsigns_db.items()])
        else:
            embed.description = "No callsigns assigned."
        channel = ctx.guild.get_channel(CALLSIGN_LIST_CHANNEL_ID)
        await (channel.send(embed=embed) if channel else ctx.send(embed=embed))

    @commands.command()
    async def nocallsign(self, ctx):
        role = ctx.guild.get_role(self.required_role_id)
        if not role:
            return await ctx.send("Error: Role not found.")
        missing = [m.mention for m in role.members if m.id not in callsigns_db]
        embed = discord.Embed(
            title="Members Without Callsigns",
            description="\n".join(missing) if missing else "All members have callsigns.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        channel = ctx.guild.get_channel(CALLSIGN_LIST_CHANNEL_ID)
        await (channel.send(embed=embed) if channel else ctx.send(embed=embed))

    @commands.command()
    async def copycallsigns(self, ctx):
        if not ctx.message.reference:
            return await ctx.send("You must reply to a callsign embed message.")

        try:
            ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except discord.NotFound:
            return await ctx.send("Message not found.")

        if not ref_msg.embeds or ref_msg.embeds[0].title != "Callsigns":
            return await ctx.send("Replied message must be a Callsigns embed.")

        added = 0
        for line in ref_msg.embeds[0].description.splitlines():
            match = re.match(r"<@(\d+)>: (.+)", line)
            if match:
                callsigns_db[int(match.group(1))] = match.group(2)
                added += 1
        await ctx.send(f"Successfully added {added} callsign(s) to the DB.")

    @commands.command()
    async def callsignadmin(self, ctx, action: str = None, member: discord.Member = None, *, callsign: str = None):
        if not any(r.id == ALLOWED_ROLE_ID for r in ctx.author.roles):
            embed = discord.Embed(title="UNAUTHORIZED", description="You are not allowed to execute this command.", color=discord.Color.red())
            await ctx.send(embed=embed)

            alert = ctx.guild.get_channel(ALERT_CHANNEL_ID)
            if alert:
                alert_embed = discord.Embed(
                    title="Attempted Use of a Restricted Command",
                    color=discord.Color.orange(),
                    timestamp=datetime.now()
                )
                alert_embed.add_field(name="User", value=ctx.author.mention, inline=False)
                alert_embed.add_field(name="Command", value=ctx.message.content, inline=False)
                alert_embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
                alert_embed.add_field(name="Jump to Message", value=f"[Click Here]({ctx.message.jump_url})", inline=False)
                await alert.send(embed=alert_embed)
            return

        if action not in ["add", "remove", "modify"] or not member or not callsign:
            return await ctx.send("Usage examples:\n!callsignadmin add @user callsign\n!callsignadmin remove @user\n!callsignadmin modify @user newcallsign")

        if action == "add":
            callsigns_db[member.id] = callsign
            await ctx.send(f"✅ Callsign `{callsign}` added for {member.mention}.")
        elif action == "remove":
            if member.id in callsigns_db:
                del callsigns_db[member.id]
                await ctx.send(f"❌ Callsign removed for {member.mention}.")
            else:
                await ctx.send(f"{member.mention} has no assigned callsign.")
        elif action == "modify":
            if member.id in callsigns_db:
                callsigns_db[member.id] = callsign
                await ctx.send(f"✏️ Callsign changed to `{callsign}` for {member.mention}.")
            else:
                await ctx.send(f"{member.mention} has no existing callsign. Use `add`.")

    async def on_member_update(self, before, after):
        role = after.guild.get_role(self.required_role_id)
        if not role:
            return
        if role in before.roles and role not in after.roles:
            if after.id in callsigns_db:
                del callsigns_db[after.id]
                print(f"Removed callsign for {after.id} (role removed)")


async def setup(bot):
    await bot.add_cog(Panel(bot))
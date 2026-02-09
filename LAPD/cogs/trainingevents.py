import discord
from discord import Embed, Colour, ButtonStyle, Interaction, Member, Permissions
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands

class CancelButton(View):
    def __init__(self, host: Member, original_message_id: int, event_type: str):
        super().__init__(timeout=None)
        self.host = host
        self.original_message_id = original_message_id
        self.event_type = event_type

    @discord.ui.button(label="Cancel", style=ButtonStyle.red)
    async def cancel_button(self, interaction: Interaction, button: Button):
        if interaction.user != self.host:
            embed = Embed(
                description=f"Only the host can cancel this {self.event_type.lower()}!",
                colour=Colour.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = Embed(
            description=f"{self.event_type} cancelled.",
            colour=Colour.blue()
        )
        await interaction.response.send_message(embed=embed, reply_to=self.original_message_id)
        button.disabled = True
        await interaction.message.edit(view=self)

class TrainingModal(Modal, title="Training Announcement"):
    def __init__(self):
        super().__init__()
        self.when = TextInput(label="When", required=True)
        self.location = TextInput(label="Location", required=True)
        self.servercode = TextInput(label="Server Code", required=True)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.notes = TextInput(label="Notes (Optional)", required=False, style=discord.TextStyle.paragraph)
        self.add_item(self.when)
        self.add_item(self.location)
        self.add_item(self.servercode)
        self.add_item(self.cohost)
        self.add_item(self.notes)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1329908997381296220)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="LAPD • Training Announcement",
            description="React if attending ✅",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Host / Helpers", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="When", value=self.when.value, inline=False)
        embed.add_field(name="Location", value=self.location.value, inline=False)
        embed.add_field(name="Server code", value=self.servercode.value, inline=False)
        embed.add_field(name="Notes", value=self.notes.value if self.notes.value else "N/A", inline=False)
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        view = CancelButton(host=interaction.user, original_message_id=None, event_type="Training")
        await channel.send(content="<@&1306380788056723578> <@&1306380827143180340>")
        message = await channel.send(embed=embed, view=view)
        view.original_message_id = message.id
        await message.edit(view=view)
        await message.add_reaction("✅")
        embed = Embed(description="Training announcement sent successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SWATTrainingModal(Modal, title="SWAT Training Announcement"):
    def __init__(self):
        super().__init__()
        self.when = TextInput(label="When", required=True)
        self.location = TextInput(label="Location", required=True)
        self.servercode = TextInput(label="Server Code", required=True)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.notes = TextInput(label="Notes (Optional)", required=False, style=discord.TextStyle.paragraph)
        self.add_item(self.when)
        self.add_item(self.location)
        self.add_item(self.servercode)
        self.add_item(self.cohost)
        self.add_item(self.notes)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1348476059036815463)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="LAPD • SWAT Training",
            description="React if attending ✅",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Host / Helpers", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="When", value=self.when.value, inline=False)
        embed.add_field(name="Location", value=self.location.value, inline=False)
        embed.add_field(name="Server code", value=self.servercode.value, inline=False)
        embed.add_field(name="Notes", value=self.notes.value if self.notes.value else "N/A", inline=False)
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        view = CancelButton(host=interaction.user, original_message_id=None, event_type="SWAT Training")
        await channel.send(content="<@&1348415029837430956>")
        message = await channel.send(embed=embed, view=view)
        view.original_message_id = message.id
        await message.edit(view=view)
        await message.add_reaction("✅")
        embed = Embed(description="SWAT Training announcement sent successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class OrientationModal(Modal, title="Orientation Announcement"):
    def __init__(self):
        super().__init__()
        self.when = TextInput(label="When", required=True)
        self.location = TextInput(label="Location", required=True)
        self.servercode = TextInput(label="Server Code", required=True)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.notes = TextInput(label="Notes (Optional)", required=False, style=discord.TextStyle.paragraph)
        self.add_item(self.when)
        self.add_item(self.location)
        self.add_item(self.servercode)
        self.add_item(self.cohost)
        self.add_item(self.notes)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1329908997381296220)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="LAPD • Orientation Announcement",
            description="React if attending ✅",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Host / Helpers", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="When", value=self.when.value, inline=False)
        embed.add_field(name="Location", value=self.location.value, inline=False)
        embed.add_field(name="Server code", value=self.servercode.value, inline=False)
        embed.add_field(name="Notes", value=self.notes.value if self.notes.value else "N/A", inline=False)
        embed.set_footer(text=f"Sent by {interaction.user.display_name}")

        view = CancelButton(host=interaction.user, original_message_id=None, event_type="Orientation")
        await channel.send(content="<@&1306380788056723578> <@&1306380858437144576>")
        message = await channel.send(embed=embed, view=view)
        view.original_message_id = message.id
        await message.edit(view=view)
        await message.add_reaction("✅")
        embed = Embed(description="Orientation announcement sent successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogOrientationModal(Modal, title="Log Orientation Result"):
    def __init__(self, trainee: Member):
        super().__init__()
        self.trainee = trainee
        self.result = TextInput(label="Result", required=True)
        self.comments = TextInput(label="Comments", required=True, style=discord.TextStyle.paragraph)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.result)
        self.add_item(self.comments)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1328036335826763939)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="Orientation • Result",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Trainee", value=self.trainee.mention, inline=False)
        embed.add_field(name="Result", value=self.result.value, inline=False)
        embed.add_field(name="Comments", value=self.comments.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(content=self.trainee.mention, embed=embed)
        embed = Embed(description="Orientation result logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogTrainingModal(Modal, title="Log Training Result"):
    def __init__(self, trainee: Member):
        super().__init__()
        self.trainee = trainee
        self.result = TextInput(label="Result", required=True)
        self.comments = TextInput(label="Comments", required=True, style=discord.TextStyle.paragraph)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.result)
        self.add_item(self.comments)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1329939121086529566)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="Training • Result",
            description=f"{self.trainee.mention} Please take your final exam.",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Trainee", value=self.trainee.mention, inline=False)
        embed.add_field(name="Result", value=self.result.value, inline=False)
        embed.add_field(name="Comments", value=self.comments.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(content=self.trainee.mention, embed=embed)
        embed = Embed(description="Training result logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogSWATTrainingModal(Modal, title="Log SWAT Training Result"):
    def __init__(self, trainee: Member):
        super().__init__()
        self.trainee = trainee
        self.result = TextInput(label="Result", required=True)
        self.comments = TextInput(label="Comments", required=True, style=discord.TextStyle.paragraph)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.result)
        self.add_item(self.comments)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1329939121086529566)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="SWAT Training • Result",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Trainee", value=self.trainee.mention, inline=False)
        embed.add_field(name="Result", value=self.result.value, inline=False)
        embed.add_field(name="Comments", value=self.comments.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(content=self.trainee.mention, embed=embed)
        embed = Embed(description="SWAT Training result logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogCertificationModal(Modal, title="Log Certification"):
    def __init__(self, trainee: Member):
        super().__init__()
        self.trainee = trainee
        self.certification = TextInput(label="Certification", required=True)
        self.result = TextInput(label="Result", required=True)
        self.comments = TextInput(label="Comments", required=True, style=discord.TextStyle.paragraph)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.certification)
        self.add_item(self.result)
        self.add_item(self.comments)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1292546024489091224)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="Certification • Result",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Trainee", value=self.trainee.mention, inline=False)
        embed.add_field(name="Certification", value=self.certification.value, inline=False)
        embed.add_field(name="Result", value=self.result.value, inline=False)
        embed.add_field(name="Comments", value=self.comments.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(content=self.trainee.mention, embed=embed)
        embed = Embed(description="Certification logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogMassShiftModal(Modal, title="Log Mass Shift Result"):
    def __init__(self):
        super().__init__()
        self.started = TextInput(label="Started at", required=True)
        self.ended = TextInput(label="Ended at", required=True)
        self.attendedusers = TextInput(label="Attended Users", required=True)
        self.promotedusers = TextInput(label="Promoted Users", required=True)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.started)
        self.add_item(self.ended)
        self.add_item(self.attendedusers)
        self.add_item(self.promotedusers)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1328036189973909655)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="LAPD • Mass Shift",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Started at", value=self.started.value, inline=False)
        embed.add_field(name="Ended at", value=self.ended.value, inline=False)
        embed.add_field(name="Attended users", value=self.attendedusers.value, inline=False)
        embed.add_field(name="Promoted users", value=self.promotedusers.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(embed=embed)
        embed = Embed(description="Mass shift result logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class LogSWATDeploymentModal(Modal, title="Log SWAT Deployment Result"):
    def __init__(self):
        super().__init__()
        self.started = TextInput(label="Started at", required=True)
        self.ended = TextInput(label="Ended at", required=True)
        self.attendedusers = TextInput(label="Attended Users", required=True)
        self.promotedusers = TextInput(label="Promoted Users", required=True)
        self.cohost = TextInput(label="Co-Host / Helpers (Optional)", required=False)
        self.add_item(self.started)
        self.add_item(self.ended)
        self.add_item(self.attendedusers)
        self.add_item(self.promotedusers)
        self.add_item(self.cohost)

    async def on_submit(self, interaction: Interaction):
        channel = interaction.client.get_channel(1348476059036815463)
        if not channel:
            embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = Embed(
            title="LAPD • SWAT Deployment",
            colour=Colour.blue()
        )
        embed.add_field(name="Host", value=interaction.user.mention, inline=False)
        embed.add_field(name="Co-Hosts", value=self.cohost.value if self.cohost.value else "N/A", inline=False)
        embed.add_field(name="Started at", value=self.started.value, inline=False)
        embed.add_field(name="Ended at", value=self.ended.value, inline=False)
        embed.add_field(name="Attended users", value=self.attendedusers.value, inline=False)
        embed.add_field(name="Promoted users", value=self.promotedusers.value, inline=False)
        embed.set_footer(text=f"Issued by {interaction.user.display_name}")

        await channel.send(embed=embed)
        embed = Embed(description="SWAT deployment result logged successfully!", colour=Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

class EventsView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Announce Training", style=ButtonStyle.green)
    async def training_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(TrainingModal())
        except Exception as e:
            embed = Embed(description=f"Error launching Training modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Announce SWAT Training", style=ButtonStyle.green)
    async def swat_training_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(SWATTrainingModal())
        except Exception as e:
            embed = Embed(description=f"Error launching SWAT Training modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Announce Orientation", style=ButtonStyle.green)
    async def orientation_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(OrientationModal())
        except Exception as e:
            embed = Embed(description=f"Error launching Orientation modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Announce Mass Shift", style=ButtonStyle.green)
    async def mass_shift_button(self, interaction: Interaction, button: Button):
        try:
            channel = interaction.client.get_channel(1292541172807635066)
            if not channel:
                embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = Embed(
                title="LAPD • Mass Shift Announcement",
                description=f"{interaction.user.mention} is hosting a **MASS SHIFT**.\n3+ votes required to start\nSWAT Officers may attend the mass shift as SWAT officer and get promoted.\nReact if attending ✅",
                colour=Colour.blue()
            )
            message = await channel.send(content="||<@&1292541838904791040>||", embed=embed)
            await message.add_reaction("✅")
            embed = Embed(description="Mass shift announcement sent successfully!", colour=Colour.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = Embed(description=f"Error sending Mass Shift announcement: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Announce SWAT Deployment", style=ButtonStyle.green)
    async def swat_deployment_button(self, interaction: Interaction, button: Button):
        try:
            channel = interaction.client.get_channel(1348476059036815463)
            if not channel:
                embed = Embed(description="Error: Target channel not found.", colour=Colour.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            embed = Embed(
                title="LAPD • SWAT Deployment Announcement",
                description=f"{interaction.user.mention} is hosting a **SWAT DEPLOYMENT**.\n3+ votes required to start\nReact if attending ✅",
                colour=Colour.blue()
            )
            message = await channel.send(content="||<@&1306381401830064201>||", embed=embed)
            await message.add_reaction("✅")
            embed = Embed(description="SWAT deployment announcement sent successfully!", colour=Colour.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = Embed(description=f"Error sending SWAT Deployment announcement: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ResultView(View):
    def __init__(self, trainee: Member = None):
        super().__init__(timeout=60)
        self.trainee = trainee
        if not trainee:
            self.log_training_button.disabled = True
            self.log_orientation_button.disabled = True
            self.log_swat_training_button.disabled = True
            self.log_certification_button.disabled = True

    @discord.ui.button(label="Log Training Result", style=ButtonStyle.blurple)
    async def log_training_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogTrainingModal(self.trainee))
        except Exception as e:
            embed = Embed(description=f"Error launching Training Result modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Log SWAT Training Result", style=ButtonStyle.blurple)
    async def log_swat_training_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogSWATTrainingModal(self.trainee))
        except Exception as e:
            embed = Embed(description=f"Error launching SWAT Training Result modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Log Orientation Result", style=ButtonStyle.blurple)
    async def log_orientation_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogOrientationModal(self.trainee))
        except Exception as e:
            embed = Embed(description=f"Error launching Orientation Result modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Log Certification", style=ButtonStyle.blurple)
    async def log_certification_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogCertificationModal(self.trainee))
        except Exception as e:
            embed = Embed(description=f"Error launching Certification modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Log Mass Shift Result", style=ButtonStyle.blurple)
    async def log_mass_shift_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogMassShiftModal())
        except Exception as e:
            embed = Embed(description=f"Error launching Mass Shift Result modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Log SWAT Deployment Result", style=ButtonStyle.blurple)
    async def log_swat_deployment_button(self, interaction: Interaction, button: Button):
        try:
            await interaction.response.send_modal(LogSWATDeploymentModal())
        except Exception as e:
            embed = Embed(description=f"Error launching SWAT Deployment Result modal: {str(e)}", colour=Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class TrainingEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="events", description="Shows the event announcement panel.")
    async def events(self, ctx: commands.Context):
        view = EventsView()
        embed = Embed(description="Event Announcement Panel", colour=Colour.blue())
        await ctx.send(embed=embed, view=view, delete_after=60)

    @commands.hybrid_command(name="result", description="Shows the result logging panel for a user or mass shift/SWAT deployment.")
    async def result(self, ctx: commands.Context, user: Member = None):
        view = ResultView(trainee=user)
        embed = Embed(
            description="Result Logging Panel" + (f" for {user.mention}" if user else ""),
            colour=Colour.blue()
        )
        await ctx.send(embed=embed, view=view, delete_after=60)

    @commands.hybrid_command(name="sync", description="Syncs slash commands for the specified guild.")
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context):
        if str(ctx.guild.id) != "1292523481539543193":
            embed = Embed(description="Error: This command can only be used in the specified guild.", colour=Colour.red())
            await ctx.send(embed=embed, delete_after=10, ephemeral=True)
            return

        try:
            synced = await ctx.bot.tree.sync(guild=discord.Object(id=1292523481539543193))
            embed = Embed(description=f"Successfully synced {len(synced)} commands for the guild!", colour=Colour.green())
            await ctx.send(embed=embed, delete_after=10, ephemeral=True)
        except Exception as e:
            embed = Embed(description=f"Error: Failed to sync commands. {str(e)}", colour=Colour.red())
            await ctx.send(embed=embed, delete_after=10, ephemeral=True)

async def setup(bot):
    await bot.add_cog(TrainingEvents(bot))

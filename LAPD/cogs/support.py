import discord
from discord.ext import commands
import json
from discord.ui import Select, View
from io import StringIO

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "tickets_data.json"
        self.load_data()
        self.bot.add_view(self.get_ticket_view())

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading tickets_data.json: {e}")
            self.data = {
                "panel_channel_id": 1451271870019014770,
                "panel_message_id": None,
                "log_channel_id": 1331018524218626100,
                "tickets": {},
                "panel_embed": {
                    "title": "** | Support**",
                    "color": 0x112255,
                    
                },
                "ticket_types": {
                    "1": {
                        "name": "General Support",
                        "category_id": 1376216650000633957,
                        "staff_role_id":1306382245895868476,
                        "embed": {
                            "title": "General Ticket",
                            "description": "Your general support ticket has been created. A team member will assist you shortly.\nPlease provide details about your issue.",
                            "color": 0x112255,
                            "author": "General Support Team",
                            "author_icon": "https://cdn.discordapp.com/icons/1292523481539543193/547df1f10a071619f4b98875a7e11aed.png?size=512",
                            "footer": "LAPD | Ticket System",
                        }
                    },
                    "2": {
                        "name": "IA Support",
                        "category_id": 1376216515191509082,
                        "staff_role_id": 1306458776181800990,
                        "embed": {
                            "title": "Internals Affairs Ticket",
                            "description": "Your IA Ticket has been created. Please send proofs of your report.",
                            "color": 0x112255,
                            "author": "Internals Affairs Team",
                            "author_icon": "https://cdn.discordapp.com/icons/1292523481539543193/547df1f10a071619f4b98875a7e11aed.png?size=512",
                            "footer": "LAPD | Ticket System",
                            
                        }
                    },
                    "3": {
                        "name": "BOT Support",
                        "category_id": 1376217124238000269,
                        "staff_role_id": 1339058176003407915,
                        "embed": {
                            "title": "BOT Ticket",
                            "description": "Your BOT ticket has been created. Please provide details about your bot issues or suggestions.",
                            "color": 0x112255,
                            "author": "BOT Team",
                            "author_icon": "https://cdn.discordapp.com/icons/1292523481539543193/547df1f10a071619f4b98875a7e11aed.png?size=512",
                            "footer": "LAPD | Ticket System",
                            
                        }
                    },
                    
                        }
                    }
                
            
            self.save_data()

    def save_data(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving tickets_data.json: {e}")

    def get_ticket_view(self):
        view = View(timeout=None)
        options = [
            discord.SelectOption(label=val["name"], value=key)
            for key, val in self.data["ticket_types"].items()
        ]
        select = Select(placeholder="Choose ticket type", options=options, custom_id="ticket_select")
        select.callback = self.ticket_callback
        view.add_item(select)
        return view

    async def ticket_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if not isinstance(interaction.data, dict) or "values" not in interaction.data or not interaction.data["values"]:
            await interaction.followup.send("Error: Invalid selection. Please try again.", ephemeral=True)
            print(f"Error in ticket_callback: Invalid interaction.data for user {interaction.user.id}")
            return
        type_key = interaction.data["values"][0]
        ticket_type = self.data["ticket_types"].get(type_key)
        if not ticket_type:
            await interaction.followup.send("Invalid ticket type selected.", ephemeral=True)
            print(f"Error in ticket_callback: Invalid ticket type {type_key} for user {interaction.user.id}")
            return

        category_id = ticket_type.get("category_id")
        category = self.bot.get_channel(category_id)
        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("Category not configured properly.", ephemeral=True)
            print(f"Error in ticket_callback: Invalid category ID {category_id} for ticket type {type_key}")
            return

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("Guild not found.", ephemeral=True)
            print(f"Error in ticket_callback: Guild not found for user {interaction.user.id}")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        staff_role_id = ticket_type.get("staff_role_id")
        staff_role = None
        if staff_role_id:
            staff_role = guild.get_role(staff_role_id)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            else:
                await interaction.followup.send("Staff role not found.", ephemeral=True)
                print(f"Error in ticket_callback: Invalid staff role ID {staff_role_id} for ticket type {type_key}")
                return

        try:
            channel_name = f"ticket-{interaction.user.name.lower()}-{ticket_type['name'].lower().replace(' ', '-')}"
            channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
        except discord.errors.Forbidden:
            await interaction.followup.send("Bot lacks permission to create channels.", ephemeral=True)
            print(f"Error in ticket_callback: Bot lacks permission to create channel for user {interaction.user.id}")
            return
        except Exception as e:
            await interaction.followup.send(f"Error creating ticket channel: {e}", ephemeral=True)
            print(f"Error in ticket_callback: Failed to create channel for user {interaction.user.id}: {e}")
            return

        self.data["tickets"][str(channel.id)] = {"type": type_key, "claimed_by": None}
        self.save_data()

        embed_data = ticket_type["embed"]
        embed = discord.Embed(
            title=embed_data.get("title", ""),
            description=embed_data.get("description", ""),
            color=embed_data.get("color", discord.Color.blue())
        )
        if embed_data.get("author"):
            embed.set_author(name=embed_data["author"], icon_url=embed_data.get("author_icon", ""))
        if embed_data.get("footer"):
            embed.set_footer(text=embed_data["footer"])
        if embed_data.get("image"):
            embed.set_image(url=embed_data["image"])
        if embed_data.get("thumbnail"):
            embed.set_thumbnail(url=embed_data["thumbnail"])

        ping = f"{staff_role.mention} " if staff_role else ""
        try:
            await channel.send(f"{interaction.user.mention} {ping}Welcome to your ticket!", embed=embed)
            await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)
        except discord.errors.Forbidden:
            await interaction.followup.send("Bot lacks permission to send messages in the ticket channel.", ephemeral=True)
            print(f"Error in ticket_callback: Bot lacks permission to send message in channel {channel.id}")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TicketCog loaded for {self.bot.user.name}")
        invalid_tickets = []
        for channel_id in self.data["tickets"]:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                invalid_tickets.append(channel_id)
        for channel_id in invalid_tickets:
            self.data["tickets"].pop(channel_id, None)
        self.save_data()

        panel_channel_id = self.data.get("panel_channel_id")
        if not panel_channel_id:
            print("WARNING: Panel channel ID not configured in tickets_data.json. Ticket panel not sent.")
            return
        channel = self.bot.get_channel(panel_channel_id)
        if not channel:
            print(f"ERROR: Panel channel {panel_channel_id} not found. Ticket panel not sent.")
            return
        view = self.get_ticket_view()
        embed_data = self.data["panel_embed"]
        embed = discord.Embed(
            title=embed_data.get("title", "Support Panel"),
            description=embed_data.get("description", "Select the type of ticket you want to create from the dropdown below."),
            color=embed_data.get("color", discord.Color.green())
        )
        if embed_data.get("author"):
            embed.set_author(name=embed_data["author"], icon_url=embed_data.get("author_icon", ""))
        if embed_data.get("footer"):
            embed.set_footer(text=embed_data["footer"])
        if embed_data.get("image"):
            embed.set_image(url=embed_data["image"])
        if embed_data.get("thumbnail"):
            embed.set_thumbnail(url=embed_data["thumbnail"])

        panel_message_id = self.data.get("panel_message_id")
        try:
            if panel_message_id:
                try:
                    msg = await channel.fetch_message(panel_message_id)
                    await msg.edit(embed=embed, view=view)
                    print(f"Ticket panel updated in channel {channel.name} (ID: {channel.id})")
                except discord.errors.NotFound:
                    msg = await channel.send(embed=embed, view=view)
                    self.data["panel_message_id"] = msg.id
                    self.save_data()
                    print(f"Ticket panel sent to channel {channel.name} (ID: {channel.id}) - new message created")
            else:
                msg = await channel.send(embed=embed, view=view)
                self.data["panel_message_id"] = msg.id
                self.save_data()
                print(f"Ticket panel sent to channel {channel.name} (ID: {channel.id})")
        except discord.errors.Forbidden:
            print(f"ERROR: Bot lacks permission to send/edit messages in panel channel {channel.name} (ID: {channel.id})")
        except Exception as e:
            print(f"ERROR: Failed to send ticket panel to channel {channel.name} (ID: {channel.id}): {e}")

    async def check_staff_role(self, ctx):
        ticket_data = self.data["tickets"].get(str(ctx.channel.id))
        if not ticket_data:
            return False
        type_key = ticket_data.get("type")
        if not type_key or type_key not in self.data["ticket_types"]:
            return False
        staff_role_id = self.data["ticket_types"][type_key].get("staff_role_id")
        if not staff_role_id:
            return False
        guild = ctx.guild
        if not guild:
            return False
        staff_role = guild.get_role(staff_role_id)
        if not staff_role:
            return False
        return staff_role in ctx.author.roles

    @commands.command(name="claim")
    async def claim(self, ctx):
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        ticket_data = self.data["tickets"].get(str(ctx.channel.id))
        if not ticket_data:
            await ctx.send("This is not a recognized ticket channel.")
            return
        try:
            ticket_data["claimed_by"] = ctx.author.id
            self.data["tickets"][str(ctx.channel.id)] = ticket_data
            self.save_data()
            await ctx.send(f"Ticket claimed by {ctx.author.mention}.")
        except Exception as e:
            await ctx.send(f"Error claiming ticket: {e}")
            print(f"Error in claim: Failed for ticket {ctx.channel.id}: {e}")

    @commands.command(name="assignclaimed")
    async def assignclaimed(self, ctx, member: discord.Member = None):
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        ticket_data = self.data["tickets"].get(str(ctx.channel.id))
        if not ticket_data:
            await ctx.send("This is not a recognized ticket channel.")
            return
        try:
            if member is None:
                member = ctx.author
            if not isinstance(member, discord.Member):
                await ctx.send("Invalid member provided.")
                print(f"Error in assignclaimed: Invalid member for ticket {ctx.channel.id}")
                return
            ticket_data["claimed_by"] = member.id
            self.data["tickets"][str(ctx.channel.id)] = ticket_data
            self.save_data()
            await ctx.send(f"Ticket claimed by {member.mention}.")
        except Exception as e:
            await ctx.send(f"Error assigning ticket: {e}")
            print(f"Error in assignclaimed: Failed for ticket {ctx.channel.id}: {e}")

    @commands.command(name="changeclaimed")
    async def changeclaimed(self, ctx, member: discord.Member):
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        ticket_data = self.data["tickets"].get(str(ctx.channel.id))
        if not ticket_data:
            await ctx.send("This is not a recognized ticket channel.")
            return
        try:
            ticket_data["claimed_by"] = member.id
            self.data["tickets"][str(ctx.channel.id)] = ticket_data
            self.save_data()
            await ctx.send(f"Ticket claim transferred to {member.mention}.")
        except Exception as e:
            await ctx.send(f"Error transferring ticket claim: {e}")
            print(f"Error in changeclaimed: Failed for ticket {ctx.channel.id}: {e}")

    @commands.command(name="add")
    async def add_user(self, ctx, member: discord.Member):
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        try:
            await ctx.channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
            await ctx.send(f"Added {member.mention} to the ticket.")
        except discord.errors.Forbidden:
            await ctx.send("Bot lacks permission to manage channel permissions.")
            print(f"Error in add_user: Bot lacks permission to manage permissions in ticket {ctx.channel.id}")

    @commands.command(name="remove")
    async def remove_user(self, ctx, member: discord.Member):
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to use this command.")
            return
        try:
            await ctx.channel.set_permissions(member, overwrite=None)
            await ctx.send(f"Removed {member.mention} from the ticket.")
        except discord.errors.Forbidden:
            await ctx.send("Bot lacks permission to manage channel permissions.")
            print(f"Error in remove_user: Bot lacks permission to manage permissions in ticket {ctx.channel.id}")

    @commands.command(name="close")
    async def close(self, ctx):
        ticket_data = self.data["tickets"].get(str(ctx.channel.id))
        if not ticket_data:
            await ctx.send("This is not a recognized ticket channel.")
            return
        if not await self.check_staff_role(ctx):
            await ctx.send("You don't have permission to close this ticket.")
            return
        try:
            await ctx.send("Closing ticket...")
            transcript = await self.generate_transcript(ctx.channel, ticket_data)
            transcript.seek(0)  # Reset file pointer
            log_channel_id = self.data.get("log_channel_id")
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id)
                if not log_channel:
                    await ctx.send(f"Warning: Log channel {log_channel_id} not found. Transcript not sent.")
                    print(f"Error in close: Log channel {log_channel_id} not found for ticket {ctx.channel.id}")
                else:
                    try:
                        file = discord.File(transcript, filename=f"transcript-{ctx.channel.name}.txt")
                        await log_channel.send(
                            f"Transcript for {ctx.channel.name} (ID: {ctx.channel.id}):",
                            file=file
                        )
                    except discord.errors.Forbidden:
                        await ctx.send("Bot lacks permission to send transcript to log channel.")
                        print(f"Error in close: Bot lacks permission to send transcript to log channel {log_channel_id}")
                    except Exception as e:
                        await ctx.send(f"Error sending transcript: {e}")
                        print(f"Error in close: Failed to send transcript to log channel {log_channel_id}: {e}")
            self.data["tickets"].pop(str(ctx.channel.id), None)
            self.save_data()
            await ctx.channel.delete()
        except discord.errors.Forbidden:
            await ctx.send("Bot lacks permission to delete channel.")
            print(f"Error in close: Bot lacks permission to delete channel {ctx.channel.id}")
        except discord.errors.NotFound:
            await ctx.send("Channel already deleted.")
            print(f"Error in close: Channel {ctx.channel.id} not found for deletion")
            self.data["tickets"].pop(str(ctx.channel.id), None)
            self.save_data()
        except Exception as e:
            await ctx.send(f"Error closing ticket: {e}")
            print(f"Error in close: Failed to close ticket {ctx.channel.id}: {e}")

    async def generate_transcript(self, channel, ticket_data):
        content = f"Transcript for {channel.name} (ID: {channel.id})\n"
        content += f"Ticket Type: {self.data['ticket_types'].get(ticket_data['type'], {'name': 'Unknown'})['name']}\n"
        claimed_by_id = ticket_data.get("claimed_by")
        if claimed_by_id:
            claimed_user = self.bot.get_user(claimed_by_id)
            content += f"Claimed By: {claimed_user.display_name if claimed_user else 'Unknown'} (ID: {claimed_by_id})\n"
        else:
            content += "Claimed By: None\n"
        content += "\n"
        try:
            async for message in channel.history(limit=None, oldest_first=True):
                content += f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author.display_name} (ID: {message.author.id}): {message.content}\n"
                for attachment in message.attachments:
                    content += f"Attachment: {attachment.url}\n"
        except discord.errors.Forbidden:
            content += "Error: Bot lacks permission to read message history.\n"
            print(f"Error in generate_transcript: Bot lacks permission to read message history in channel {channel.id}")
        except Exception as e:
            content += f"Error generating transcript: {e}\n"
            print(f"Error in generate_transcript: Failed for channel {channel.id}: {e}")
        return StringIO(content)

async def setup(bot):

    await bot.add_cog(Tickets(bot))
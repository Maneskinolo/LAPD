import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timezone
import asyncio
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeInputModal(discord.ui.Modal):
    def __init__(self, title, user_id, action, cog):
        super().__init__(title=title)
        self.user_id = user_id
        self.action = action
        self.cog = cog
        self.add_item(discord.ui.TextInput(
            label="Time (in minutes)",
            placeholder="Enter time in minutes",
            required=True,
            style=discord.TextStyle.short
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            minutes = int(self.children[0].value)
            if minutes <= 0:
                raise ValueError("Time must be positive.")
            data = self.cog.load_shifts()
            user_data = data["users"].setdefault(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            
            if self.action == "add":
                user_data["total_duration"] += minutes
                user_data["history"].append({
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": None,
                    "duration": minutes,
                    "note": "Added via admin"
                })
                action_text = f"Added {minutes} minutes to"
            else:  # remove
                user_data["total_duration"] = max(0, user_data["total_duration"] - minutes)
                user_data["history"].append({
                    "start": datetime.now(timezone.utc).isoformat(),
                    "end": None,
                    "duration": -minutes,
                    "note": "Removed via admin"
                })
                action_text = f"Removed {minutes} minutes from"
            
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="Shift Updated",
                description=f"{action_text} <@{self.user_id}>'s shift duration.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except ValueError as e:
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in TimeInputModal: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class AdminButtons(discord.ui.View):
    def __init__(self, user_id, cog):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="Start Shift", style=discord.ButtonStyle.green)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not await self.cog.has_shift_admin(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = self.cog.load_shifts()
            user_data = data["users"].setdefault(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            if user_data["active"]:
                embed = discord.Embed(
                    title="Shift Already Active",
                    description=f"<@{self.user_id}> is already on shift.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            user_data["active"] = True
            user_data["start_time"] = datetime.now(timezone.utc).isoformat()
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="Shift Started",
                description=f"Started shift for <@{self.user_id}>.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in start_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Stop Shift", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not await self.cog.has_shift_admin(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = self.cog.load_shifts()
            user_data = data["users"].setdefault(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            if not user_data["active"]:
                embed = discord.Embed(
                    title="No Active Shift",
                    description=f"<@{self.user_id}> is not on shift.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            start_time = datetime.fromisoformat(user_data["start_time"])
            duration = int((datetime.now(timezone.utc) - start_time).total_seconds() // 60)
            user_data["total_duration"] += duration
            user_data["active"] = False
            user_data["history"].append({
                "start": user_data["start_time"],
                "end": datetime.now(timezone.utc).isoformat(),
                "duration": duration
            })
            del user_data["start_time"]
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="Shift Stopped",
                description=f"Stopped shift for <@{self.user_id}>. Duration: {duration} minutes.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in stop_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Add Time", style=discord.ButtonStyle.blurple)
    async def add_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.cog.has_shift_admin(interaction.user):
            await interaction.response.send_message(embed=discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        await interaction.response.send_modal(TimeInputModal("Add Shift Time", self.user_id, "add", self.cog))

    @discord.ui.button(label="Remove Time", style=discord.ButtonStyle.grey)
    async def remove_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.cog.has_shift_admin(interaction.user):
            await interaction.response.send_message(embed=discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            ), ephemeral=True)
            return
        await interaction.response.send_modal(TimeInputModal("Remove Shift Time", self.user_id, "remove", self.cog))

    @discord.ui.button(label="Show Shifts", style=discord.ButtonStyle.secondary)
    async def show_shifts_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not await self.cog.has_shift_admin(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = self.cog.load_shifts()
            user_data = data["users"].get(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            history = user_data["history"]
            history_text = []
            for i, entry in enumerate(history[:10], 1):  # Limit to last 10 shifts
                start = datetime.fromisoformat(entry["start"]).strftime('%Y-%m-%d %H:%M:%S UTC')
                end = datetime.fromisoformat(entry["end"]).strftime('%Y-%m-%d %H:%M:%S UTC') if entry["end"] else "N/A"
                duration = entry["duration"]
                note = entry.get("note", "")
                history_text.append(f"{i}. Start: {start}, End: {end}, Duration: {duration} mins{note and f' ({note})' or ''}")
            embed = discord.Embed(
                title=f"Shift History for <@{self.user_id}>",
                description="\n".join(history_text) or "No shift history.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Total Duration", value=f"{user_data['total_duration']} minutes")
            embed.add_field(name="Active", value="Yes" if user_data["active"] else "No")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in show_shifts_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class ActiveButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.blurple)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if not await self.cog.has_shift_basic(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Basic or Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        try:
            data = self.cog.load_shifts()
            active_users = [
                f"<@{user_id}> (Started: {datetime.fromisoformat(user_data['start_time']).strftime('%Y-%m-%d %H:%M:%S UTC')})"
                for user_id, user_data in data["users"].items() if user_data["active"]
            ]
            embed = discord.Embed(
                title="Active Shifts",
                description="\n".join(active_users) if active_users else "No active shifts.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Error in refresh_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

class LeaderboardButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.blurple)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if not await self.cog.has_shift_basic(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Basic or Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        try:
            data = self.cog.load_shifts()
            guild = interaction.guild
            shift_users = []
            for member in guild.members:
                if await self.cog.has_shift_basic(member):
                    user_id = str(member.id)
                    total_duration = data["users"].get(user_id, {"total_duration": 0})["total_duration"]
                    shift_users.append((member, total_duration))
            
            shift_users.sort(key=lambda x: x[1], reverse=True)
            leaderboard = [
                f"{i+1}. {member.mention}: {duration} minutes"
                for i, (member, duration) in enumerate(shift_users[:100])  # Limit to top 100
            ]
            embed = discord.Embed(
                title="Shift Leaderboard",
                description="\n".join(leaderboard) if leaderboard else "No users with shift permissions.",
                color=discord.Color.gold(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, view=self)
        except Exception as e:
            logger.error(f"Error in refresh_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

class EraseButtons(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)  # Timeout after 60 seconds
        self.cog = cog

    @discord.ui.button(label="Confirm Erase", style=discord.ButtonStyle.red)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not await self.cog.has_shift_admin(interaction.user):
            embed = discord.Embed(
                title="Permission Denied",
                description="You need the Shift Admin role to use this.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = {"users": {}}
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="All Shift Data Erased",
                description="All shift data for all users has been erased.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.stop()  # Disable buttons after confirmation
        except Exception as e:
            logger.error(f"Error in confirm_button: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="Erase Cancelled",
            description="Shift data erasure cancelled.",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        self.stop()  # Disable buttons after cancellation

class ShiftButtons(discord.ui.View):
    def __init__(self, user_id, cog):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="Start Shift", style=discord.ButtonStyle.green)
    async def start_shift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="Error",
                description="Only the command issuer can use these buttons.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = self.cog.load_shifts()
            user_data = data["users"].setdefault(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            if user_data["active"]:
                embed = discord.Embed(
                    title="Shift Already Active",
                    description="You are already on shift.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            user_data["active"] = True
            user_data["start_time"] = datetime.now(timezone.utc).isoformat()
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="Shift Started",
                description="Your shift has started.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in start_shift: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="End Shift", style=discord.ButtonStyle.red)
    async def end_shift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != self.user_id:
            embed = discord.Embed(
                title="Error",
                description="Only the command issuer can use these buttons.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        try:
            data = self.cog.load_shifts()
            user_data = data["users"].setdefault(str(self.user_id), {"active": False, "total_duration": 0, "history": []})
            if not user_data["active"]:
                embed = discord.Embed(
                    title="No Active Shift",
                    description="You are not currently on shift.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            start_time = datetime.fromisoformat(user_data["start_time"])
            duration = int((datetime.now(timezone.utc) - start_time).total_seconds() // 60)
            user_data["total_duration"] += duration
            user_data["active"] = False
            user_data["history"].append({
                "start": user_data["start_time"],
                "end": datetime.now(timezone.utc).isoformat(),
                "duration": duration
            })
            del user_data["start_time"]
            self.cog.save_shifts(data)
            embed = discord.Embed(
                title="Shift Ended",
                description=f"Your shift has ended. Duration: {duration} minutes.",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in end_shift: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class Shift(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shift_file = "shifts.json"
        self.shift_basic_role_id = 1292541838904791040  # Shift Basic role ID
        self.shift_admin_role_id = 1383535858698948799  # Shift Admin role ID
        self.load_shifts()
        logger.info("Shift cog initialized")

    def load_shifts(self):
        """Load shift data from shifts.json or initialize an empty structure."""
        try:
            if not os.path.exists(self.shift_file):
                logger.info("Creating new shifts.json")
                with open(self.shift_file, 'w') as f:
                    json.dump({"users": {}}, f)
                return {"users": {}}
            with open(self.shift_file, 'r') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "users" not in data:
                    logger.warning("Invalid or missing 'users' key in shifts.json, resetting")
                    data = {"users": {}}
                    with open(self.shift_file, 'w') as f:
                        json.dump(data, f, indent=4)
                return data
        except json.JSONDecodeError:
            logger.error("Corrupted shifts.json, resetting to default")
            data = {"users": {}}
            with open(self.shift_file, 'w') as f:
                json.dump(data, f, indent=4)
            return data
        except Exception as e:
            logger.error(f"Error loading shifts.json: {e}")
            return {"users": {}}

    def save_shifts(self, data):
        """Save shift data to shifts.json."""
        try:
            with open(self.shift_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving shifts.json: {e}")

    async def has_shift_basic(self, member: discord.Member):
        """Check if a member has the Shift Basic or Shift Admin role."""
        has_role = any(role.id in [self.shift_basic_role_id, self.shift_admin_role_id] for role in member.roles)
        logger.info(f"Checking shift_basic for {member.id}: {has_role}")
        return has_role

    async def has_shift_admin(self, member: discord.Member):
        """Check if a member has the Shift Admin role."""
        has_role = any(role.id == self.shift_admin_role_id for role in member.roles)
        logger.info(f"Checking shift_admin for {member.id}: {has_role}")
        return has_role

    @commands.hybrid_group(name="duty", invoke_without_command=True)
    async def duty(self, ctx: commands.Context):
        await ctx.defer()
        try:
            embed = discord.Embed(
                title="Duty Command",
                description="Use subcommands: `manage`, `active`, `admin`, `leaderboard`, `erase`.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in duty: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @duty.command(name="manage")
    @app_commands.describe()
    async def duty_manage(self, ctx: commands.Context):
        await ctx.defer()
        if not await self.has_shift_basic(ctx.author):
            embed = discord.Embed(
                title="UNAUTHORIZED",
                description="You need the Shift Basic or Shift Admin role to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            data = self.load_shifts()
            user_id = str(ctx.author.id)
            user_data = data["users"].setdefault(user_id, {"active": False, "total_duration": 0, "history": []})
            total_duration = user_data["total_duration"]

            embed = discord.Embed(
                title="Shift Management",
                description="Use the buttons below to start or end your shift.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Total Duty Time", value=f"{total_duration} minutes")
            embed.add_field(name="Active", value="Yes" if user_data["active"] else "No")
            await ctx.send(embed=embed, view=ShiftButtons(ctx.author.id, self))
        except Exception as e:
            logger.error(f"Error in duty_manage: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @duty.command(name="active")
    @app_commands.describe()
    async def duty_active(self, ctx: commands.Context):
        await ctx.defer()
        if not await self.has_shift_basic(ctx.author):
            embed = discord.Embed(
                title="UNAUTHORIZED",
                description="You need the Shift Basic or Shift Admin role to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            data = self.load_shifts()
            active_users = [
                f"<@{user_id}> (Started: {datetime.fromisoformat(user_data['start_time']).strftime('%Y-%m-%d %H:%M:%S UTC')})"
                for user_id, user_data in data["users"].items() if user_data["active"]
            ]
            embed = discord.Embed(
                title="Active Shifts",
                description="\n".join(active_users) if active_users else "No active shifts.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed, view=ActiveButtons(self))
        except Exception as e:
            logger.error(f"Error in duty_active: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @duty.command(name="admin")
    @app_commands.describe(user="The user to manage shifts for")
    async def duty_admin(self, ctx: commands.Context, user: discord.Member):
        await ctx.defer()
        if not await self.has_shift_admin(ctx.author):
            embed = discord.Embed(
                title="UNAUTHORIZED",
                description="You need the Shift Admin role to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            embed = discord.Embed(
                title=f"Shift admin : {user.display_name}",
                description="Use the buttons below.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed, view=AdminButtons(user.id, self))
        except Exception as e:
            logger.error(f"Error in duty_admin: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @duty.command(name="leaderboard")
    @app_commands.describe()
    async def duty_leaderboard(self, ctx: commands.Context):
        await ctx.defer()
        if not await self.has_shift_basic(ctx.author):
            embed = discord.Embed(
                title="UNAUTHORIZED",
                description="You need the Shift Basic or Shift Admin role to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            data = self.load_shifts()
            guild = ctx.guild
            shift_users = []
            for member in guild.members:
                if await self.has_shift_basic(member):
                    user_id = str(member.id)
                    total_duration = data["users"].get(user_id, {"total_duration": 0})["total_duration"]
                    shift_users.append((member, total_duration))
            
            shift_users.sort(key=lambda x: x[1], reverse=True)
            leaderboard = [
                f"{i+1}. {member.mention}: {duration} minutes"
                for i, (member, duration) in enumerate(shift_users[:100])  # Limit to top 100
            ]
            embed = discord.Embed(
                title="Shift Leaderboard",
                description="\n".join(leaderboard) if leaderboard else "No users with shift permissions.",
                color=discord.Color.gold(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed, view=LeaderboardButtons(self))
        except Exception as e:
            logger.error(f"Error in duty_leaderboard: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @duty.command(name="erase")
    @app_commands.describe()
    async def duty_erase(self, ctx: commands.Context):
        await ctx.defer()
        if not await self.has_shift_admin(ctx.author):
            embed = discord.Embed(
                title="UNAUTHORIZED",
                description="You need the Shift Admin role to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            embed = discord.Embed(
                title="Erase All Shift Data",
                description="Confirm or cancel erasing all shift data for all users.",
                color=discord.Color.blue(),
                timestamp=datetime.now(timezone.utc)
            )
            await ctx.send(embed=embed, view=EraseButtons(self))
        except Exception as e:
            logger.error(f"Error in duty_erase: {e}")
            embed = discord.Embed(
                title="Error",
                description="An unexpected error occurred.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shift(bot))
    logger.info("Shift cog loaded")

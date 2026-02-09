
from discord.ext import commands
import random
import discord

class AssignTO(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.assignments = {}  # Store persistent assignments

    @commands.command(name='assignto')
    async def assign_to(self, ctx):
        prob_officer_role_id = 1306380788056723578
        to_role_id = 1470145093825466449
        loa_role_id = 1470145287967211720
        target_channel_id = 1323293471829786665

        guild = ctx.guild
        target_channel = guild.get_channel(target_channel_id)

        if not target_channel:
            await ctx.send("Error: Target channel not found.")
            return

        prob_officers = [member for member in guild.members if prob_officer_role_id in [role.id for role in member.roles]]
        tos = [member for member in guild.members if to_role_id in [role.id for role in member.roles]]

        if not prob_officers:
            await ctx.send("Error: No Probationary Officers found.")
            return
        if not tos:
            await ctx.send("Error: No TOs found.")
            return

        # Clean up assignments: Remove Probationary Officers who no longer have the role
        current_prob_ids = {member.id for member in prob_officers}
        self.assignments = {
            to: [prob for prob in assigned_probs if prob.id in current_prob_ids]
            for to, assigned_probs in self.assignments.items()
        }

        # Filter out probationary officers already assigned, on LOA role, or with LOA in nickname
        unassigned_probs = []
        for prob in prob_officers:
            if prob.id in [p.id for to in self.assignments.values() for p in to]:
                continue
            if loa_role_id in [role.id for role in prob.roles]:
                continue
            if prob.nick and "loa" in prob.nick.lower():
                continue
            unassigned_probs.append(prob)

        # Perform new assignments only for unassigned probationary officers
        random.shuffle(unassigned_probs)
        temp_assignments = {to: self.assignments.get(to, []) for to in tos}  # Keep existing assignments

        while unassigned_probs:
            for to in tos:
                if unassigned_probs:
                    temp_assignments[to].append(unassigned_probs.pop())

        # Update persistent assignments
        self.assignments = temp_assignments

        embed = discord.Embed(
            title="TOs & Probationary Officers Assignation",
            description="Here is the list of all Probationary Officers with their assigned TOs.",
            color=discord.Color.blue()
        )

        for to, assigned_probs in self.assignments.items():
            if not assigned_probs:
                embed.add_field(
                    name=f"{to.display_name} ({to.mention})",
                    value="No Probationary Officers assigned.",
                    inline=False
                )
                continue

            field_value = ""
            for prob in assigned_probs:
                loa_status = " (On LOA)" if (loa_role_id in [role.id for role in prob.roles] or 
                                             (prob.nick and "loa" in prob.nick.lower())) else ""
                field_value += f"- {prob.mention}{loa_status}\n"
            if len(field_value) > 1024:
                field_value = field_value[:1000] + "... (truncated)"
            embed.add_field(
                name=f"{to.display_name} ({to.mention})",
                value=field_value,
                inline=False
            )

        if not any(self.assignments.values()):
            embed.add_field(
                name="Assignments",
                value="No assignments could be made.",
                inline=False
            )

        try:
            await target_channel.send(embed=embed)
            await ctx.send(f"Assignments have been posted in {target_channel.mention}.")
        except discord.HTTPException as e:
            await ctx.send(f"Error sending embed: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        prob_officer_role_id = 1306380788056723578
        loa_role_id = 1470145287967211720
        target_channel_id = 1323293471829786665
        target_channel = after.guild.get_channel(target_channel_id)

        if not target_channel:
            return

        updated = False

        # Check if Probationary Officer role was removed
        if prob_officer_role_id in [role.id for role in before.roles] and \
           prob_officer_role_id not in [role.id for role in after.roles]:
            self.assignments = {
                to: [prob for prob in assigned_probs if prob.id != after.id]
                for to, assigned_probs in self.assignments.items()
            }
            updated = True

        # Check if member gained LOA role
        if loa_role_id not in [role.id for role in before.roles] and \
           loa_role_id in [role.id for role in after.roles] and \
           prob_officer_role_id in [role.id for role in after.roles]:
            self.assignments = {
                to: [prob for prob in assigned_probs if prob.id != after.id]
                for to, assigned_probs in self.assignments.items()
            }
            updated = True

        # Check if nickname changed to include LOA
        before_nick = before.nick or ""
        after_nick = after.nick or ""
        if "loa" not in before_nick.lower() and "loa" in after_nick.lower() and \
           prob_officer_role_id in [role.id for role in after.roles]:
            self.assignments = {
                to: [prob for prob in assigned_probs if prob.id != after.id]
                for to, assigned_probs in self.assignments.items()
            }
            updated = True

        # Update assignments display if any changes were made
        if updated:
            embed = discord.Embed(
                title="TOs & Probationary Officers Assignation",
                description="Here is the updated list of all Probationary Officers with their assigned TOs.",
                color=discord.Color.blue()
            )

            for to, assigned_probs in self.assignments.items():
                if not assigned_probs:
                    embed.add_field(
                        name=f"{to.display_name} ({to.mention})",
                        value="No Probationary Officers assigned.",
                        inline=False
                    )
                    continue

                field_value = ""
                for prob in assigned_probs:
                    loa_status = " (On LOA)" if (loa_role_id in [role.id for role in prob.roles] or 
                                                 (prob.nick and "loa" in prob.nick.lower())) else ""
                    field_value += f"- {prob.mention}{loa_status}\n"
                    if len(field_value) > 1024:
                        field_value = field_value[:1000] + "... (truncated)"
                    embed.add_field(
                        name=f"{to.display_name} ({to.mention})",
                        value=field_value,
                        inline=False
                    )

            if not any(self.assignments.values()):
                embed.add_field(
                    name="Assignments",
                    value="No assignments could be made.",
                    inline=False
                )

            try:
                await target_channel.send(embed=embed)
            except discord.HTTPException as e:
                print(f"Error sending embed: {e}")

async def setup(bot):
    await bot.add_cog(AssignTO(bot))
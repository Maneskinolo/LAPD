from IPython import embed
from audioop import add
import discord
from discord.ext import commands
from datetime import datetime
import os
import asyncio
import json
import time
import re
import dotenv
from dotenv import load_dotenv
load_dotenv()
from collections import Counter

# Configuration
GUILD_ID = 1292523481539543193  # Your guild ID
# Load environment variables and token
TOKEN = os.getenv("DISCORD_TOKEN") # Replace with your bot token
SHARED_PANEL_CHANNEL = 1292541250775290097 # Shared panel channel ID for Sub-Divisions
ANNOUNCEMENT_CHANNEL_ID = 1292532379411284081
ALLOWED_ROLE_IDS = [1337050305153470574, 1361565373593292851]
HR_ROLE_IDS = [1306380163013017700,1339058176003407915]
AUTOROLE_ROLE_ID = 1292541718033596558
# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="!", intents=intents)
# Runtime globals
loaded_cogs = []
sleep_mode = False
auto_role_enabled = False
role_to_assign = None

bot.event
async def on_ready():
    print(f'{bot.prefix} Bot is ready! Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Connected to {len(bot.guilds)} guild(s).')
    print (f'{bot.id}')

@bot.command(name='roleall')
@commands.has_permissions(administrator=True)  # Restrict to admins
async def roleall(ctx, role1: discord.Role, role2: discord.Role):
    # Check if the bot has permission to manage roles
    if not ctx.guild.me.guild_permissions.manage_roles:
        await ctx.send("I don't have permission to manage roles!")
        return

    # Check if the bot's highest role is above both role1 and role2
    if ctx.guild.me.top_role <= role1 or ctx.guild.me.top_role <= role2:
        await ctx.send("I can't assign roles higher than or equal to my highest role!")
        return

    # Check if the command issuer's highest role is above both role1 and role2
    if ctx.author.top_role <= role1 or ctx.author.top_role <= role2:
        await ctx.send("You can't manage roles higher than or equal to your highest role!")
        return

    # Get all members with role1
    members_with_role1 = [member for member in ctx.guild.members if role1 in member.roles]

    if not members_with_role1:
        await ctx.send(f"No members have the role {role1.name}.")
        return

    # Assign role2 to members with role1
    success_count = 0
    for member in members_with_role1:
        try:
            await member.add_roles(role2)
            success_count += 1
        except discord.Forbidden:
            await ctx.send(f"Failed to assign {role2.name} to {member.name} due to insufficient permissions.")
            return
        except Exception as e:
            await ctx.send(f"An error occurred while assigning {role2.name} to {member.name}: {e}")
            return

    await ctx.send(f"Successfully assigned {role2.name} to {success_count} member(s) with {role1.name}.")

# Error handling for the command
@bot.command()
async def say(ctx, *, message: str):
    allowed_user_id = 1335497299773620287
    banned_user_id = 1030197824702398547
    
    if ctx.author.id == banned_user_id:
        embed = discord.Embed(
            title="UNAUTHORIZED",
            description=f"Hello <@{banned_user_id}>, you have been banned from using this command, and dont you dare ping and beg me again to unban./n **Reason** Self Explanatory : 'There are only 2 genders, Men and woman, *cry about it*'",
            colour=discord.Color.red()
        )
        embed.set_footer(text="Los Angeles Police Department")
        await ctx.send(embed=embed)
        return
    
    if ctx.author.id == allowed_user_id or any(role.id in HR_ROLE_IDS for role in ctx.author.roles):
        try:
            await ctx.message.delete()
            await ctx.send(message)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages.", delete_after=5)
    else:
        await ctx.send("❌ You don't have the required role or permission to use this command.", delete_after=5)

@bot.command(name="announce")
async def announce(ctx, *, message: str):
    if not any(role.id in ALLOWED_ROLE_IDS for role in ctx.author.roles):
        try:
            await ctx.message.delete()
            await ctx.author.send("This is a restricted command, only Bot Tamers and Board of Chiefs members can use it.")
        except discord.Forbidden:
            pass
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if channel is None:
        await ctx.author.send(f"❌ Announcement channel with ID {ANNOUNCEMENT_CHANNEL_ID} not found.")
        return

    try:
        await channel.send(message)
        await ctx.author.send(f"✅ Announcement sent to {channel.mention}.")
    except discord.Forbidden:
        await ctx.author.send(f"❌ I don't have permission to send messages in {channel.mention}.")

@bot.event
async def on_member_join(member: discord.Member):
    global auto_role_enabled, role_to_assign
    if auto_role_enabled and role_to_assign:
        try:
            role = member.guild.get_role(AUTOROLE_ROLE_ID)
            if role:
                await member.add_roles(role)
                print(f"✅ Assigned {role.name} to {member.name}.")
            else:
                print(f"❌ Role with ID {AUTOROLE_ROLE_ID} not found.")
        except discord.Forbidden:
            print(f"❌ Failed to assign {role.name} to {member.name}. Bot lacks permissions.")
        except discord.HTTPException as e:
            print(f"❌ Failed to assign role: {e}")

@bot.command()
async def test(ctx):
    print("Command executed once")
    await ctx.send("Test command executed.")

import discord
from discord.ext import commands

# Ak používaš hybridný prístup, môžeš mať aj slash verziu – ale tu ideme čisto prefix

import discord
from discord.ext import commands

# Ak používaš hybridný prístup, môžeš mať aj slash verziu – ale tu ideme čisto prefix




@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount < 1 or amount > 100:
        await ctx.send("Please specify a number between 1 and 100.", delete_after=5)
        return
    try:
        await ctx.channel.purge(
            limit=amount + 1,
            check=lambda m: not m.pinned
        )
        await ctx.send(f"Successfully deleted {amount} non-pinned message(s).", delete_after=5)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to delete messages.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"❌ Failed to purge messages: {e}", delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need 'Manage Messages' permission.", delete_after=5)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I need 'Manage Messages' permission.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the number of messages to purge.", delete_after=5)
    elif isinstance(error, commands.CheckFailure):
        return  # Handled by globally_block_banned_users or sleep mode check
    else:
        print(f"Purge error: {error}")
        await ctx.send(f"Error: {str(error)}", delete_after=5)

@bot.command()
async def hello(ctx):
    await ctx.send("You thought I would say hello didn't you, bitch?")

@bot.command()
async def autorole(ctx, status: str, role: discord.Role = None):
    global auto_role_enabled, role_to_assign
    if status.lower() == "on":
        if role:
            role_to_assign = role
            auto_role_enabled = True
            await ctx.send(f"✅ Auto-role is now **ON**. The role {role.mention} will be assigned to all new members.")
        else:
            await ctx.send("❌ You must **mention** a role (e.g., `!autorole on @Role`).")
    elif status.lower() == "off":
        auto_role_enabled = False
        role_to_assign = None
        await ctx.send("🚫 Auto-role is now **OFF**.")
    else:
        await ctx.send("❌ Please specify either `on` or `off`.")

@bot.command()
async def currentautorole(ctx):
    global auto_role_enabled, role_to_assign
    if auto_role_enabled and role_to_assign:
        role = ctx.guild.get_role(AUTOROLE_ROLE_ID)
        await ctx.send(f"✅ Auto-role is **ON**. The assigned role is {role.mention}.")
    else:
        await ctx.send("🚫 Auto-role is **OFF**.")

@bot.command()
async def nick(ctx, member: discord.Member, *, nickname: str = None):
    try:
        await ctx.message.delete()
        old_nick = member.nick or member.name
        await member.edit(nick=nickname)
        if nickname:
            await ctx.send(f"✅ Changed {member.mention}'s nickname from '{old_nick}' to '{nickname}'.")
        else:
            await ctx.send(f"✅ Reset {member.mention}'s nickname to default.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to change this member's nickname.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"❌ Failed to change nickname: {e}", delete_after=5)

@bot.command()
@commands.is_owner()
async def stop(ctx):
    global sleep_mode
    try:
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name="Waiting for developers to start me.."
        )
        await bot.change_presence(status=discord.Status.idle, activity=activity)
        sleep_mode = True
        embed = discord.Embed(
            title="Bot Entering Sleep Mode",
            description="The bot is now in sleep mode. All commands are disabled except for the bot owner.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        cogs_list = loaded_cogs if loaded_cogs else ["None"]
        embed.add_field(
            name="Disabled Cogs",
            value=", ".join(cogs_list),
            inline=False
        )
        embed.set_footer(text=f"Command used: stop | User ID: {ctx.author.id}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error setting sleep mode: {e}")

@bot.command()
@commands.is_owner()
async def start(ctx):
    global sleep_mode
    try:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Los Angeles Police Department"
        )
        await bot.change_presence(status=discord.Status.dnd, activity=activity)
        sleep_mode = False
        embed = discord.Embed(
            title="Bot Activated",
            description="The bot is now active and all commands are available.",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        cogs_list = loaded_cogs if loaded_cogs else ["None"]
        embed.add_field(
            name="Enabled Cogs",
            value=", ".join(cogs_list),
            inline=True
        )
        embed.set_footer(text=f"Command used: start | User ID: {ctx.author.id}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error activating bot: {e}")

async def load_extensions():
    global loaded_cogs
    loaded_cogs.clear()   # make sure list is empty

# Load cogs
async def load_extensions():
    global loaded_cogs
    cogs = [
        "cogs.jishaku",
        "cogs.trainingevents",
        "cogs.support",
        "cogs.lapd",
        "cogs.embedbuilder",
        "cogs.panel",
        "cogs.shift",
        "cogs.assignto",
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog} cog")
            loaded_cogs.append(cog.split(".")[-1])
        except Exception as e:
            print(f"Failed to load {cog} cog: {e}")

# Main function
async def main():
    await load_extensions()
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {e}")
    
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
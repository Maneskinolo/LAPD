import discord
from discord.ext import commands
import re
import uuid
import asyncio
import logging
from datetime import datetime

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbedBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_color = discord.Color.blue()
        self.default_large_image = None
        self.embed_store = {}

    class EmbedModal(discord.ui.Modal, title="Modify Custom Embed"):
        def __init__(self, default_color, default_large_image, embed_id, existing_embed):
            super().__init__()
            self.default_color = default_color
            self.default_large_image = default_large_image
            self.embed_id = embed_id

            default_title = existing_embed.title if existing_embed else ""
            default_description = existing_embed.description if existing_embed else ""
            default_footer = existing_embed.footer.text if existing_embed and existing_embed.footer else ""
            default_large_image = existing_embed.image.url if existing_embed and existing_embed.image else ""
            default_color = f"#{existing_embed.color.value:06x}" if existing_embed else ""

            self.name = discord.ui.TextInput(
                label="Name",
                placeholder="Enter the title for the embed",
                max_length=256,
                required=True,
                default=default_title
            )
            self.description = discord.ui.TextInput(
                label="Description",
                placeholder="Enter the description",
                style=discord.TextStyle.paragraph,
                max_length=4000,
                required=True,
                default=default_description
            )
            self.footer = discord.ui.TextInput(
                label="Footer",
                placeholder="Enter footer text",
                max_length=2048,
                required=False,
                default=default_footer
            )
            self.large_image = discord.ui.TextInput(
                label="Large Image URL",
                placeholder="Enter image URL for large image or send the image",
                max_length=2048,
                required=False,
                default=default_large_image
            )
            self.color = discord.ui.TextInput(
                label="Color (Hex)",
                placeholder="Enter hex color (e.g., #FF0000)",
                max_length=7,
                required=False,
                default=default_color
            )

            self.add_item(self.name)
            self.add_item(self.description)
            self.add_item(self.footer)
            self.add_item(self.large_image)
            self.add_item(self.color)

        async def on_submit(self, interaction: discord.Interaction):
            color = self.default_color
            if self.color.value:
                try:
                    hex_color = self.color.value.lstrip('#')
                    if re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
                        color = discord.Color(int(hex_color, 16))
                    else:
                        embed = discord.Embed(
                            title="Error: Invalid Hex Color",
                            description="The provided hex color format is invalid. Using default color.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="Command", value="Modify Embed", inline=True)
                        embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                        embed.add_field(name="Details", value=f"Invalid input: {self.color.value}", inline=False)
                        embed.timestamp = datetime.utcnow()
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        logger.warning(f"User {interaction.user.id} provided invalid hex color: {self.color.value}")
                except ValueError:
                    embed = discord.Embed(
                        title="Error: Invalid Hex Color",
                        description="The provided hex color is invalid. Using default color.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Command", value="Modify Embed", inline=True)
                    embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                    embed.add_field(name="Details", value=f"Invalid input: {self.color.value}", inline=False)
                    embed.timestamp = datetime.utcnow()
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    logger.error(f"User {interaction.user.id} provided invalid hex color value: {self.color.value}")

            embed = discord.Embed(
                title=self.name.value,
                description=self.description.value,
                color=color
            )

            if self.footer.value:
                embed.set_footer(text=self.footer.value)

            large_image_url = self.large_image.value or self.default_large_image
            if large_image_url:
                if re.match(r'^https?://[^\s<>"\'\[\]]+\.(?:png|jpg|jpeg|gif|webp)$', large_image_url, re.IGNORECASE):
                    embed.set_image(url=large_image_url)
                    logger.info(f"Set large image for embed: {large_image_url}")
                else:
                    embed = discord.Embed(
                        title="Error: Invalid Large Image URL",
                        description="The provided large image URL is invalid. Embed created without large image.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Command", value="Modify Embed", inline=True)
                    embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                    embed.add_field(name="Details", value=f"Invalid URL: {large_image_url}", inline=False)
                    embed.timestamp = datetime.utcnow()
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    logger.warning(f"Invalid large image URL: {large_image_url}")

            total_length = len(self.name.value) + len(self.description.value) + (len(self.footer.value) if self.footer.value else 0)
            if total_length > 6000:
                embed = discord.Embed(
                    title="Error: Embed Content Too Long",
                    description="The embed content exceeds Discord's 6000-character limit!",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Modify Embed", inline=True)
                embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                embed.add_field(name="Details", value=f"Character count: {total_length}", inline=False)
                embed.timestamp = datetime.utcnow()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                logger.error(f"Embed content too long for user {interaction.user.id}: {total_length} characters")
                return

            self.cog.embed_store[self.embed_id] = embed
            try:
                await interaction.channel.send(embed=embed)
                await interaction.response.send_message(
                    f"Embed modified successfully! Embed ID: {self.embed_id}",
                    ephemeral=True
                )
                logger.info(f"Embed modified by user {interaction.user.id}, ID: {self.embed_id}")
            except discord.Forbidden:
                embed = discord.Embed(
                    title="Error: Insufficient Permissions",
                    description="I lack permission to send messages in this channel.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Modify Embed", inline=True)
                embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
                embed.add_field(name="Details", value=f"Channel: {interaction.channel.id}", inline=False)
                embed.timestamp = datetime.utcnow()
                await interaction.response.send_message(embed=embed, ephemeral=True)
                logger.error(f"Bot lacks permission to send embed in channel {interaction.channel.id}")

        async def on_error(self, interaction: discord.Interaction, error: Exception):
            embed = discord.Embed(
                title="Error: Modal Processing Failed",
                description="An error occurred while processing the embed. Please try again.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="Modify Embed", inline=True)
            embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
            embed.add_field(name="Details", value=f"Error: {str(error)}", inline=False)
            embed.timestamp = datetime.utcnow()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.error(f"Error in modal for user {interaction.user.id}: {str(error)}")

    class ModifyButton(discord.ui.View):
        def __init__(self, default_color, default_large_image, embed_id, embed, cog):
            super().__init__()
            self.default_color = default_color
            self.default_large_image = default_large_image
            self.embed_id = embed_id
            self.embed = embed
            self.cog = cog

        @discord.ui.button(label="Modify Embed", style=discord.ButtonStyle.secondary, custom_id=f"modify_button_{uuid.uuid4()}")
        async def modify_embed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            modal = self.cog.EmbedModal(self.default_color, self.default_large_image, self.embed_id, self.embed)
            modal.cog = self.cog
            await interaction.response.send_modal(modal)

    async def ask_question(self, ctx, question, max_length, required=True, default=None):
        await ctx.send(question)
        try:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0
            )
            content = response.content.strip()
            if not content and required:
                embed = discord.Embed(
                    title="Error: Required Field Missing",
                    description="This field is required. Please try again.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Embed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Question: {question}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                return await self.ask_question(ctx, question, max_length, required, default)
            if content and len(content) > max_length:
                embed = discord.Embed(
                    title="Error: Character Limit Exceeded",
                    description=f"Input exceeds {max_length} character limit. Please try again.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Embed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Length: {len(content)}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                return await self.ask_question(ctx, question, max_length, required, default)
            return content if content else default
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Error: Timeout",
                description="Timed out waiting for response. Embed creation cancelled.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="Embed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Question: {question}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"User {ctx.author.id} timed out on question: {question}")
            return None

    async def ask_image(self, ctx, question):
        await ctx.send(question)
        try:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=60.0
            )
            # Allow skipping with an empty message
            if not response.content and not response.attachments:
                logger.info(f"User {ctx.author.id} skipped large image by sending empty message")
                return None
            # Check for attachments
            if not response.attachments:
                embed = discord.Embed(
                    title="Error: No Image Attached",
                    description="No image attached! Please upload an image or send an empty message to skip.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Embed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Content: {response.content}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                logger.warning(f"User {ctx.author.id} sent message without attachment: {response.content}")
                return await self.ask_image(ctx, question)
            # Get the first attachment
            attachment = response.attachments[0]
            # Verify content type is an image
            if attachment.content_type and attachment.content_type.startswith('image/'):
                if attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    logger.info(f"User {ctx.author.id} uploaded valid image: {attachment.url}")
                    return attachment.url
                else:
                    embed = discord.Embed(
                        title="Error: Invalid Image Format",
                        description="Invalid image format! Please upload a PNG, JPG, JPEG, GIF, or WEBP file.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Command", value="Embed", inline=True)
                    embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                    embed.add_field(name="Details", value=f"Filename: {attachment.filename}", inline=False)
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed, ephemeral=True)
                    logger.warning(f"User {ctx.author.id} uploaded invalid image format: {attachment.filename}")
                    return await self.ask_image(ctx, question)
            else:
                embed = discord.Embed(
                    title="Error: Invalid Attachment",
                    description="Attachment is not an image! Please upload a valid image file.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Embed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Filename: {attachment.filename}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                logger.warning(f"User {ctx.author.id} uploaded non-image attachment: {attachment.filename}")
                return await self.ask_image(ctx, question)
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="Error: Timeout",
                description="Timed out waiting for image. Embed creation cancelled.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="Embed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Question: {question}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"User {ctx.author.id} timed out on image upload")
            return None

    async def create_or_modify_embed(self, ctx, embed_id=None, existing_embed=None):
        title = await self.ask_question(
            ctx,
            "1/5 Title?",
            max_length=256,
            required=True,
            default=existing_embed.title if existing_embed else None
        )
        if title is None:
            return

        description = await self.ask_question(
            ctx,
            "2/5 Description? ",
            max_length=4000,
            required=True,
            default=existing_embed.description if existing_embed else None
        )
        if description is None:
            return

        footer = await self.ask_question(
            ctx,
            "3/5 Footer?",
            max_length=2048,
            required=False,
            default=existing_embed.footer.text if existing_embed and existing_embed.footer else None
        )
        if footer is None:
            return

        large_image = await self.ask_image(
            ctx,
            "4/5 Large Image? "
        )
        if large_image is None and ctx.channel.permissions_for(ctx.guild.me).send_messages:
            return

        color_input = await self.ask_question(
            ctx,
            "5/5 Color (Hex, e.g., #FF0000)? ",
            max_length=7,
            required=False,
            default=f"#{existing_embed.color.value:06x}" if existing_embed else None
        )
        if color_input is None:
            return

        color = self.default_color
        if color_input:
            try:
                hex_color = color_input.lstrip('#')
                if re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
                    color = discord.Color(int(hex_color, 16))
                else:
                    embed = discord.Embed(
                        title="Error: Invalid Hex Color",
                        description="Invalid hex color format! Using default color.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Command", value="Embed", inline=True)
                    embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                    embed.add_field(name="Details", value=f"Input: {color_input}", inline=False)
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed, ephemeral=True)
                    logger.warning(f"User {ctx.author.id} provided invalid hex color: {color_input}")
            except ValueError:
                embed = discord.Embed(
                    title="Error: Invalid Hex Color",
                    description="Invalid hex color! Using default color.",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="Embed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Input: {color_input}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                logger.error(f"User {ctx.author.id} provided invalid hex color value: {color_input}")

        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        if footer:
            embed.set_footer(text=footer)

        large_image_url = large_image or self.default_large_image
        if large_image_url:
            embed.set_image(url=large_image_url)
            logger.info(f"Set large image for embed: {large_image_url}")

        total_length = len(title) + len(description) + (len(footer) if footer else 0)
        if total_length > 6000:
            embed = discord.Embed(
                title="Error: Embed Content Too Long",
                description="Embed content exceeds Discord's 6000-character limit!",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="Embed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Character count: {total_length}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"Embed content too long for user {ctx.author.id}: {total_length} characters")
            return

        try:
            await ctx.channel.send(embed=embed)
            new_embed_id = embed_id or str(uuid.uuid4())
            self.embed_store[new_embed_id] = embed
            await ctx.send(
                f"Embed {'modified' if embed_id else 'created'} successfully! Embed ID: {new_embed_id}",
                ephemeral=True
            )
            logger.info(f"Embed {'modified' if embed_id else 'created'} by user {ctx.author.id}, ID: {new_embed_id}")
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error: Insufficient Permissions",
                description="Failed to send embed: I lack permission to send messages in this channel.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="Embed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Channel: {ctx.channel.id}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"Bot lacks permission to send embed in channel {ctx.channel.id}")

    @commands.command(name="embed")
    @commands.has_permissions(send_messages=True, embed_links=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def embed_command(self, ctx: commands.Context):
        await self.create_or_modify_embed(ctx)

    @commands.command(name="copyembed")
    @commands.has_permissions(send_messages=True, embed_links=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def copy_embed(self, ctx: commands.Context, message_id: int):
        try:
            message = await ctx.channel.fetch_message(message_id)
            if not message.embeds:
                embed = discord.Embed(
                    title="Error: No Embeds Found",
                    description="No embeds found in the specified message!",
                    color=discord.Color.red()
                )
                embed.add_field(name="Command", value="copyembed", inline=True)
                embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
                embed.add_field(name="Details", value=f"Message ID: {message_id}", inline=False)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed, ephemeral=True)
                logger.warning(f"No embeds found in message {message_id} for user {ctx.author.id}")
                return

            embed = message.embeds[0]
            embed_id = str(uuid.uuid4())
            self.embed_store[embed_id] = embed
            await ctx.send(f"Embed copied successfully! Use `!pasteembed {embed_id}` to paste it.", ephemeral=True)
            logger.info(f"Embed copied by user {ctx.author.id}, ID: {embed_id}")
        except discord.NotFound:
            embed = discord.Embed(
                title="Error: Message Not Found",
                description="Message not found! Please check the message ID.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="copyembed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Message ID: {message_id}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"Message {message_id} not found for user {ctx.author.id}")
        except discord.Forbidden:
            embed = discord.Embed(
                title="Error: Insufficient Permissions",
                description="I don't have permission to access that message!",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="copyembed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Message ID: {message_id}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.error(f"Bot lacks permission to access message {message_id} for user {ctx.author.id}")

    @commands.command(name="pasteembed")
    @commands.has_permissions(send_messages=True, embed_links=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def paste_embed(self, ctx: commands.Context, embed_id: str):
        embed = self.embed_store.get(embed_id)
        if not embed:
            embed = discord.Embed(
                title="Error: Invalid Embed ID",
                description="Invalid or expired embed ID!",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="pasteembed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Embed ID: {embed_id}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.warning(f"Invalid or expired embed ID {embed_id} for user {ctx.author.id}")
            return

        await ctx.send(embed=embed)
        await ctx.send(f"Embed pasted successfully! ID: {embed_id}", ephemeral=True)
        logger.info(f"Embed pasted by user {ctx.author.id}, ID: {embed_id}")

    @commands.command(name="modifyembed")
    @commands.has_permissions(send_messages=True, embed_links=True)
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def modify_embed(self, ctx: commands.Context, embed_id: str):
        embed = self.embed_store.get(embed_id)
        if not embed:
            embed = discord.Embed(
                title="Error: Invalid Embed ID",
                description="Invalid or expired embed ID!",
                color=discord.Color.red()
            )
            embed.add_field(name="Command", value="modifyembed", inline=True)
            embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
            embed.add_field(name="Details", value=f"Embed ID: {embed_id}", inline=False)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed, ephemeral=True)
            logger.warning(f"Invalid or expired embed ID {embed_id} for user {ctx.author.id}")
            return

        view = self.ModifyButton(self.default_color, self.default_large_image, embed_id, embed, self)
        await ctx.send("Click the button to modify the embed!", view=view, ephemeral=True)
        logger.info(f"Modify embed initiated by user {ctx.author.id}, ID: {embed_id}")

    @embed_command.error
    @copy_embed.error
    @paste_embed.error
    @modify_embed.error
    async def command_error(self, ctx: commands.Context, error: commands.CommandError):
        embed = discord.Embed(
            title="Error: Command Execution Failed",
            description="An error occurred while executing the command.",
            color=discord.Color.red()
        )
        embed.add_field(name="Command", value=ctx.command.name, inline=True)
        embed.add_field(name="User ID", value=str(ctx.author.id), inline=True)
        embed.timestamp = datetime.utcnow()

        if isinstance(error, commands.MissingPermissions):
            embed.description = "You need `send_messages` and `embed_links` permissions to use this command."
            embed.add_field(name="Details", value="Missing user permissions.", inline=False)
            logger.error(f"User {ctx.author.id} lacks permissions for {ctx.command.name}")
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = "I need `send_messages` and `embed_links` permissions to execute this command."
            embed.add_field(name="Details", value=f"Channel: {ctx.channel.id}", inline=False)
            logger.error(f"Bot lacks permissions for {ctx.command.name} in channel {ctx.channel.id}")
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"Missing required argument: {error.param.name}"
            embed.add_field(name="Details", value=f"Missing: {error.param.name}", inline=False)
            logger.error(f"Missing argument {error.param.name} for {ctx.command.name} by user {ctx.author.id}")
        else:
            embed.add_field(name="Details", value=f"Error: {str(error)}", inline=False)
            logger.error(f"Error in {ctx.command.name} for user {ctx.author.id}: {str(error)}")

        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedBuilder(bot))

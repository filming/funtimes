import discord
from discord import app_commands
from discord.ext import commands

import logging
from typing import *

from utils.decorators.is_initial_interaction_author import is_initial_interaction_author

logger = logging.getLogger("discord")

class CustomHelpCommand(commands.MinimalHelpCommand):
	""" A custom help command implementation. """

	async def send_bot_help(
		self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
	) -> None:
		""" Handle help requests for the main help page.

		This method generates and sends an embed with buttons for each category 
		of commands. It is displayed when the user requests for general help.
		"""

		help_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title="Select A Category To Get Started!",
		)
		
		help_view = HelpView(self, self.context.author)
		
		await self.context.reply(embed=help_embed, view=help_view)

	async def send_command_help(self, command: commands.Command) -> None:
		""" Handle help requests for a specific command.

		This method generates and sends an embed containing the command's usage, 
		aliases, and required permissions.
		"""

		embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title=command.qualified_name,
			description=command.help or "No description provided"
		)

		if command.aliases:
			embed.add_field(
				name="Aliases", value=f"```{', '.join(command.aliases)}```", inline=False
			)

		example_usage = f"```{self.context.prefix}{command.qualified_name} {command.signature}```"
		embed.add_field(name="Usage", value=example_usage, inline=False)

		permissions_text = "```"

		if "required_bot_permissions" in command.extras:
			permissions_text += "\nBot:"
			for curr_permission in command.extras["required_bot_permissions"]:
				permissions_text += f"\n∙ {curr_permission}"
		
		if "required_user_permissions" in command.extras:
			permissions_text += "\n\nUser:"
			for curr_permission in command.extras["required_user_permissions"]:
				permissions_text += f"\n∙ {curr_permission}"
		
		permissions_text += "```"

		if permissions_text != "``````":
			embed.add_field(name="Required Permissions", value=permissions_text, inline=False)

		await self.context.reply(embed=embed)

	async def send_group_help(self, group: commands.Group) -> None:
		""" Handle help requests for a command group.
		
		This method generates and sends an embed with information about a command 
		group and its subcommands.
		"""

		embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title=f"{group.qualified_name} Commands",
			description=group.help or "No description provided",
		)

		subcommands_text = "```"
		for command in group.walk_commands():
			subcommands_text += f"\n\n{self.context.prefix}{command.qualified_name} {command.signature}\n ∙ {command.help or "No description provided"}"
		subcommands_text += "```"

		embed.add_field(name="Sub-Commands", value=subcommands_text, inline=False)

		await self.context.reply(embed=embed)
	
	async def send_cog_help(self, cog: commands.Cog) -> None:
		""" Handle help requests for cogs.

		This method is intentionally left blank as help should be provided in the
		send_bot_help(), send_command_help(), and send_group_help() levels.
		"""

		pass

	async def send_error_message(self, error: str):
		""" Handle errors that arrive from help command invocation. """

		embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title="Error", 
			description=error
		)

		await self.context.reply(embed=embed)

class Help(commands.Cog):
	""" A cog to handle custom help commands. 
	
	This cog sets up a custom help command for the bot. It also allows the help
	command to be accessed through slash commands.
	"""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.custom_help_command = CustomHelpCommand()
		self.custom_help_command.cog = self
		self.bot.help_command = self.custom_help_command
	
	@app_commands.command(name="help")
	async def help_slash(self, interaction):
		""" Initiate the text-based help command. """

		context = await self.bot.get_context(interaction)
		self.custom_help_command.context = context
		await self.custom_help_command.send_bot_help(self.bot.help_command.get_bot_mapping())

async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(Help(bot))

class HomeButtonView(discord.ui.View):
	"""A view with a home button.

	This is a subclass of discord.ui.View. It provides a home button that,
	when pressed, allows the user to return to the initial help message.
	"""

	def __init__(
		self, 
		initial_interaction_author: Union[discord.User, discord.Member], 
		home_msg_content: str, 
		home_msg_embeds: discord.Embed, 
		home_msg_view: discord.ui.View
	) -> None:
		super().__init__(timeout=180)
		self.initial_interaction_author = initial_interaction_author
		self.home_msg_content = home_msg_content
		self.home_msg_embeds = home_msg_embeds
		self.home_msg_view = home_msg_view
	
	@discord.ui.button(
		label="Home", emoji="🏠", style=discord.ButtonStyle.danger, row=1
	)
	@is_initial_interaction_author
	async def home_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the home button click event. """

		await interaction.response.edit_message(
			content=self.home_msg_content, 
			embeds=self.home_msg_embeds, 
			view=self.home_msg_view
		)

class BackButtonkHomeButtonView(HomeButtonView):
	"""A view with back and home buttons. 
	
	This is a subclass of HomeButtonView. It provides a back button that when
	pressed, allows the user to return to the previous message state.
	"""

	def __init__(
		self, 
		initial_interaction_author: Union[discord.User, discord.Member], 
		home_msg_content: str, 
		home_msg_embeds: discord.Embed,
		home_msg_view: discord.ui.View, 
		prev_msg_content: str, 
		prev_msg_embeds: discord.Embed, 
		prev_msg_view: discord.ui.View
	) -> None:
		super().__init__(
			initial_interaction_author, home_msg_content, home_msg_embeds, home_msg_view
		)
		self.prev_msg_content = prev_msg_content
		self.prev_msg_embeds = prev_msg_embeds
		self.prev_msg_view = prev_msg_view
	
	@discord.ui.button(
		label="Back", emoji="⬅️", style=discord.ButtonStyle.blurple, row=1
	)
	@is_initial_interaction_author
	async def back_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the back button click event. """

		await interaction.response.edit_message(
			content=self.prev_msg_content, 
			embeds=self.prev_msg_embeds, 
			view=self.prev_msg_view
		)

class HelpUtilityView(HomeButtonView):
	"""A view with utility subcategory buttons. 
	
	This is a subclass of HomeButtonView. It provides buttons that will
	redirect the user to specific subcategories.
	"""

	@discord.ui.button(label="Bot", emoji="🤖", style=discord.ButtonStyle.blurple, row=0)
	@is_initial_interaction_author
	async def help_utility_bot_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the utility subcategory bot button click event."""

		await interaction.response.defer()
		
		utility_bot_commands_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"), title="Utility: Bot"
		)

		command_list = ["invite", "discord"]
		description_text = "Use `$help <command>` for more info.\n```"

		for command in command_list:
			description_text += f"\n∙ {command}"
		
		description_text += "```"
		
		utility_bot_commands_embed.description = description_text

		utility_bot_commands_view = BackButtonkHomeButtonView(
			self.initial_interaction_author, 
			self.home_msg_content, 
			self.home_msg_embeds, 
			self.home_msg_view, 
			interaction.message.content, 
			interaction.message.embeds, button.view
		)

		await interaction.message.edit(
			embed=utility_bot_commands_embed, view=utility_bot_commands_view
		)

	@discord.ui.button(
		label="Server", emoji="🌎", style=discord.ButtonStyle.blurple, row=0
	)
	@is_initial_interaction_author
	async def help_utility_guild_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the utility subcategory guild button click event."""

		await interaction.response.defer()

		utility_guild_commands_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"), title="Utility: Server",
		)

		command_list = ["member-status", "server-info"]
		description_text = "Use `$help <command>` for more info.\n```"

		for command in command_list:
			description_text += f"\n∙ {command}"
		
		description_text += "```"
		
		utility_guild_commands_embed.description = description_text

		utility_guild_commands_view = BackButtonkHomeButtonView(
			self.initial_interaction_author, 
			self.home_msg_content, 
			self.home_msg_embeds, 
			self.home_msg_view, 
			interaction.message.content, 
			interaction.message.embeds, button.view)

		await interaction.message.edit(
			embed=utility_guild_commands_embed, view=utility_guild_commands_view
		)

	@discord.ui.button(
		label="User", emoji="🧑", style=discord.ButtonStyle.blurple, row=0
	)
	@is_initial_interaction_author
	async def help_utility_user_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the utility subcategory user button click event."""

		await interaction.response.defer()

		utility_user_commands_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"), title="Utility: User",
		)

		command_list = ["avatar", "banner", "remind"]
		description_text = "Use `$help <command>` for more info.\n```"

		for command in command_list:
			description_text += f"\n∙ {command}"
		
		description_text += "```"
		
		utility_user_commands_embed.description = description_text

		utility_user_commands_view = BackButtonkHomeButtonView(
			self.initial_interaction_author, 
			self.home_msg_content, 
			self.home_msg_embeds, 
			self.home_msg_view, 
			interaction.message.content, 
			interaction.message.embeds, 
			button.view
		)

		await interaction.message.edit(
			embed=utility_user_commands_embed, view=utility_user_commands_view
		)

class HelpView(discord.ui.View):
	"""A view with main category buttons. 
	
	This is a subclass of discord.ui.View. It provides buttons that will
	redirect the user to specific main category help pages.
	"""

	def __init__(
		self, 
		custom_help_command: CustomHelpCommand, 
		initial_interaction_author: Union[discord.User, discord.Member]
	) -> None:
		super().__init__(timeout=180)
		self.custom_help_command = custom_help_command
		self.initial_interaction_author = initial_interaction_author

	@discord.ui.button(
		label="Admin", emoji="🚨", style=discord.ButtonStyle.blurple, row=0
	)
	@is_initial_interaction_author
	async def help_admin_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for admin category in the main help view."""

		await interaction.response.defer()

		admin_commands_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"), title="Admin",
		)

		command_list = ["sync", "reload", "shutdown"]
		description_text = "Use `$help <command>` for more info.\n```"
		
		for command in command_list:
			description_text += f"\n∙ {command}"
		
		description_text += "```"

		admin_commands_embed.description = description_text

		admin_commands_view = HomeButtonView(
			self.initial_interaction_author, 
			interaction.message.content, 
			interaction.message.embeds, 
			button.view
		)

		await interaction.message.edit(
			embed=admin_commands_embed, view=admin_commands_view
		)
	
	@discord.ui.button(
		label="Economy", emoji="💰", style=discord.ButtonStyle.blurple, row=1
	)
	@is_initial_interaction_author
	async def help_economy_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for economy category in the main help view."""

		await interaction.response.defer()

	@discord.ui.button(label="Fun", emoji="🤣", style=discord.ButtonStyle.blurple, row=0)
	@is_initial_interaction_author
	async def help_fun_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for fun category in the main help view."""

		await interaction.response.defer()

	@discord.ui.button(
		label="Level", emoji="🏆", style=discord.ButtonStyle.blurple, row=1
	)
	@is_initial_interaction_author
	async def help_level_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for level category in the main help view."""

		await interaction.response.defer()

	@discord.ui.button(
		label="Moderation", emoji="🚫", style=discord.ButtonStyle.blurple, row=0
	)
	@is_initial_interaction_author
	async def help_moderation_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for moderation category in the main help view."""

		await interaction.response.defer()

	@discord.ui.button(
		label="Utility", emoji="🛠️", style=discord.ButtonStyle.blurple, row=1
	)
	@is_initial_interaction_author
	async def help_utility_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for utility category in the main help view."""

		await interaction.response.defer()

		help_utility_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title="Utility",
			description="**Choose A Sub-Category!**"
		)

		help_utility_view = HelpUtilityView(
			self.initial_interaction_author, 
			interaction.message.content, 
			interaction.message.embeds, 
			button.view
		)

		await interaction.message.edit(embed=help_utility_embed, view=help_utility_view)
	
	@discord.ui.button(
		label="Invite FunTimes", emoji="✨", style=discord.ButtonStyle.success, row=2
	)
	@is_initial_interaction_author
	async def help_invite_bot_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for invite category in the main help view."""
		
		await interaction.response.defer()

		help_invite_bot_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title="🔗 __Invite FunTimes Bot__ 🔗",
			description=f"**▶️ [Click here to add FunTimes to your server!]({self.custom_help_command.cog.bot.config.invite_link_bot})**",
			url=self.custom_help_command.cog.bot.config.invite_link_bot
		)
		help_invite_bot_embed.set_footer(
			text="Bring FunTimes features to your own servers!"
		)

		help_invite_bot_view = HomeButtonView(
			self.initial_interaction_author, 
			interaction.message.content, 
			interaction.message.embeds, 
			button.view
		)

		await interaction.message.edit(
			embed=help_invite_bot_embed, 
			view=help_invite_bot_view
		)
	
	@discord.ui.button(
		label="Join Discord", emoji="✨", style=discord.ButtonStyle.success, row=2
	)
	@is_initial_interaction_author
	async def help_invite_discord_button(
		self, interaction: discord.Interaction, button: discord.ui.Button
	) -> None:
		"""Handle the button click event for discord category in the main help view."""

		await interaction.response.defer()

		help_invite_discord_embed = discord.Embed(
			colour=discord.Colour.from_str("#8308f7"),
			title="🔗 __Join FunTimes Discord Server__ 🔗",
			description=f"**▶️ [Click here to join the FunTimes discord!]({self.custom_help_command.cog.bot.config.invite_link_guild})**",
			url=self.custom_help_command.cog.bot.config.invite_link_guild
		)
		help_invite_discord_embed.set_footer(
			text="Join our community for support and fun discussions!"
		)

		help_invite_discord_view = HomeButtonView(
			self.initial_interaction_author, 
			interaction.message.content, 
			interaction.message.embeds, 
			button.view
		)

		await interaction.message.edit(
			embed=help_invite_discord_embed, view=help_invite_discord_view
		)

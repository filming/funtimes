from discord.ext import commands

import logging

from utils.decorators.is_bot_admin import BotAdminCheckFailure

logger = logging.getLogger("discord")


class OnCommandError(commands.Cog):
	"""Cog for handling global command errors."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.ignored = (commands.CommandNotFound,)

	@commands.Cog.listener()
	async def on_command_error(
		self, ctx: commands.Context, error: commands.CommandError
	) -> None:
		"""Listen for errors triggered by text commands.

		This method is automatically called when a text-command error occurs. 
		It handles the error based on its type and logs the relevant information.
		"""

		# This prevents any commands with local handlers being handled here in on_command_error.
		if hasattr(ctx.command, "on_error"):
			return

		# This prevents any cogs with an overwritten cog_command_error being handled here.
		cog = ctx.cog
		if cog:
			if cog._get_overridden_method(cog.cog_command_error) is not None:
				return

		# Allows us to check for original exceptions raised and sent to CommandInvokeError.
		# If nothing is found. We keep the exception passed to on_command_error.
		error = getattr(error, "original", error)

		# Anything in ignored will return and prevent anything happening.
		if isinstance(error, self.ignored):
			return

		elif isinstance(error, BotAdminCheckFailure):
			logger.warning(
				"BotAdminCheckFailure: %s (UserID: %s, GuildID: %s) attempted to run the '%s' command while not being a bot admin.",
				ctx.author,
				ctx.author.id,
				ctx.guild.id if ctx.guild else None,
				ctx.command,
			)
			await ctx.reply(
				f"Sorry! You must be a bot admin to be able to run the {ctx.command} command."
			)

		elif isinstance(error, commands.NoPrivateMessage):
			logger.warning(
				"%s (UserID: %s, GuildID: %s) attempted to run the '%s' command inside of private messages.",
				ctx.author,
				ctx.author.id,
				None,
				ctx.command,
			)
			await ctx.reply("Sorry! This command may only be used inside of a server.")

		# This logs all errors that aren't handled above
		else:
			logger.error(
				"The following undealt with exception was raised: %s",
				error,
				exc_info=error,
			)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnCommandError(bot))

from discord.ext import commands

from typing import Callable

from utils.errors import BotAdminCheckFailure


def is_bot_admin() -> Callable[[commands.Context], bool]:
	"""Check if the user is a bot admin and raise an error if not.

	Returns a decorator that checks if the invoking user is a bot admin.
	Raises BotAdminCheckFailure if the user is not a bot admin.
	"""

	def predicate(ctx: commands.Context) -> bool:
		if str(ctx.author.id) in ctx.bot.config.bot_user_groups["admin"]:
			return True

		raise BotAdminCheckFailure(f"{ctx.author} is not a bot admin.")

	return commands.check(predicate)

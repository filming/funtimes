from discord.ext import commands


class BotAdminCheckFailure(commands.CheckFailure):
	"""Exception raised when a command is invoked by a user who is not a bot admin.

	Inherits from 'commands.CheckFailure'.
	"""

	pass


class InitialAuthorCheckFailure(commands.CheckFailure):
	"""Exception raised when a user is not the initial author of an interaction.

	Inherits from 'commands.CheckFailure'.
	"""

	pass

from discord.ext import commands

import logging

logger = logging.getLogger("discord")


class OnReady(commands.Cog):
	"""Cog for handling ready events from Discord."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.first_ready_event = False

	@commands.Cog.listener()
	async def on_ready(self) -> None:
		"""Process ready events that are receieved from Discord.

		This listener is notified when the client is done preparing the data received from Discord.
		"""

		# Using a flag to make sure this only gets ran once as its not guaranteed that this method only gets ran once.
		if not self.first_ready_event:
			logger.info("Bot '%s' has started successfully.", self.bot.user.name)
			self.first_ready_event = True


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnReady(bot))

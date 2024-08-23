import discord
from discord.ext import commands

import logging

logger = logging.getLogger("discord")


class OnMessage(commands.Cog):
	"""Cog for handling message events."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@commands.Cog.listener()
	async def on_message(self, message: discord.Message) -> None:
		"""Process messages that are received through the bot."""
		pass


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(OnMessage(bot))

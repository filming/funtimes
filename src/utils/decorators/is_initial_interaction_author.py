def is_initial_interaction_author(func):
	"""Check if the interaction user is the initial interaction author.

	Returns a decorator that checks if the interaction user is the initial interaction author.
	Invokes the associated function if they are and displays an ephemeral message if they are not.
	"""

	async def wrapper(self, interaction, button):
		if interaction.user == self.initial_interaction_author:
			await func(self, interaction, button)
		else:
			await interaction.response.send_message(
				"Sorry, only the person who asked for help can use this!",
				ephemeral=True,
			)

	return wrapper

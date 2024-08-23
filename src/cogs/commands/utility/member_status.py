import discord
from discord.ext import commands


class MemberStatus(commands.Cog):
	"""Cog to check the current status of members in the server."""

	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	@commands.hybrid_command(
		name="member-status", aliases=["memberstatus", "userstatus", "members", "users"]
	)
	@commands.guild_only()
	async def member_status(self, ctx: commands.Context) -> None:
		"""Provides the current statuses of members in this server."""

		if not ctx.author.bot:
			online_members, idle_members, dnd_members, offline_members = 0, 0, 0, 0

			for member in ctx.guild.members:
				if member.status == discord.Status.online:
					online_members += 1
				elif member.status == discord.Status.idle:
					idle_members += 1
				elif member.status in (
					discord.Status.dnd,
					discord.Status.do_not_disturb,
				):
					dnd_members += 1
				else:
					offline_members += 1

			total_members = ctx.guild.member_count

			member_status_embed = discord.Embed(
				colour=discord.Colour.from_str("#8308f7"),
				title=f"{ctx.guild.name} Member Statuses",
			)
			member_status_embed.add_field(
				name="🟢 Online",
				value=f"{online_members} {'member is' if online_members == 1 else 'members are'} online.",
				inline=False,
			)
			member_status_embed.add_field(
				name="🟠 Idle",
				value=f"{idle_members} {'member is' if idle_members == 1 else 'members are'} idle.",
				inline=False,
			)
			member_status_embed.add_field(
				name="🔴 Do Not Disturb",
				value=f"{dnd_members} {'member is' if dnd_members == 1 else 'members are'} in do not disturb.",
				inline=False,
			)
			member_status_embed.add_field(
				name="🟣 Offline / Invisible",
				value=f"{offline_members} {'member is' if offline_members == 1 else 'members are'} offline.",
				inline=False,
			)
			member_status_embed.set_footer(text=f"Server Member Count: {total_members}")

			await ctx.reply(embed=member_status_embed)


async def setup(bot: commands.Bot) -> None:
	await bot.add_cog(MemberStatus(bot))

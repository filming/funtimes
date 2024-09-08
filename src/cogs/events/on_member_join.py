import discord
from discord.ext import commands


class OnMemberJoin(commands.Cog):
    """A cog that handles member join events and related functions."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Handle a user when they join a guild."""

        if member.guild.id == 856417327175958528:  # FunTimes Server
            funtimes_guild = self.bot.get_guild(856417327175958528)

            role_categories = [
                funtimes_guild.get_role(856417327175958529),
                funtimes_guild.get_role(856417327188148246),
                funtimes_guild.get_role(856417327188148251),
            ]
            await member.add_roles(*role_categories)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnMemberJoin(bot))

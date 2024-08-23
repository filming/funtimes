from discord.ext import commands

import logging

from utils.decorators.is_bot_admin import is_bot_admin

logger = logging.getLogger("discord")


class Shutdown(commands.Cog):
    """Cog for shutting down the bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        aliases=["sd"], extras={"required_user_permissions":["funtimes_bot_admin"]}
    )
    @is_bot_admin()
    async def shutdown(self, ctx: commands.Context) -> None:
        """Shut down the bot. Can only be used by bot admins."""

        await ctx.send(f"{self.bot.application.name} is now shutting down.")
        await self.bot.close()

        logger.info(
            "Bot '%s' is now shutting down. Requested by %s (UserID: %s, GuildID: %s)",
            self.bot.application.name,
            ctx.author,
            ctx.author.id,
            ctx.guild.id if ctx.guild else None,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Shutdown(bot))

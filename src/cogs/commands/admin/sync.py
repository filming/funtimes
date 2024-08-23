from discord.ext import commands

import logging

from utils.decorators.is_bot_admin import is_bot_admin

logger = logging.getLogger("discord")


class Sync(commands.Cog):
    """Cog for handling the syncing of app commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.is_syncing_testing = False
        self.is_syncing_global = False
        self.is_clearing_testing = False
        self.is_clearing_global = False

    @commands.group(name="sync")
    @is_bot_admin()
    async def sync(self, ctx: commands.Context) -> None:
        """Group command for managing sync commands."""

        if ctx.invoked_subcommand is None:
            await ctx.send("Use `sync <local/global/clear>`")

    @sync.command(
        name="local", extras={"required_user_permissions":["funtimes_bot_admin"]}
    )
    @is_bot_admin()
    async def sync_local(self, ctx: commands.Context) -> None:
        """Sync app commands to the testing guild."""

        if not self.is_syncing_testing:
            self.is_syncing_testing = True

            self.bot.tree.copy_global_to(guild=self.bot.config.testing_guild)
            await self.bot.tree.sync(guild=self.bot.config.testing_guild)

            logger.info(
                "App commands have been synced to the testing guild by %s (UserID: %s).",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply("App commands have been synced to the testing guild.")

            self.is_syncing_testing = False
        else:
            logger.warning(
                "%s (UserID: %s) tried to sync app commands to the testing guild, however a syncing process is already ongoing.",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply(
                "Bot is already in the process of syncing app commands to the testing guild."
            )

    @sync.command(
        name="global", extras={"required_user_permissions":["funtimes_bot_admin"]}
    )
    @is_bot_admin()
    async def sync_global(self, ctx: commands.Context) -> None:
        """Sync app commands globally."""

        if not self.is_syncing_global:
            self.is_syncing_global = True

            await self.bot.tree.sync(guild=None)
            logger.info(
                "App commands have been synced globally by %s (UserID: %s).",
                ctx.author,
                ctx.author.id,
            )

            await ctx.reply("App commands have been synced globally.")

            self.is_syncing_global = False

        else:
            logger.warning(
                "%s (UserID: %s) tried to globally sync app commands, however a syncing process is already ongoing.",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply(
                "Bot is already in the process of globally syncing app commands."
            )

    @sync.group(name="clear")
    @is_bot_admin()
    async def sync_clear(self, ctx: commands.Context) -> None:
        """Group command for managing sync clear commands."""

        if ctx.invoked_subcommand is None:
            await ctx.send("Use `sync clear <local/global>`")

    @sync_clear.command(
        name="local", extras={"required_user_permissions":["funtimes_bot_admin"]}
    )
    @is_bot_admin()
    async def sync_clear_local(self, ctx: commands.Context) -> None:
        """Remove all app commands from the testing guild and sync the bot."""

        if not self.is_clearing_testing:
            self.is_clearing_testing = True

            self.bot.tree.clear_commands(guild=self.bot.config.testing_guild)
            await self.bot.tree.sync(guild=self.bot.config.testing_guild)

            logger.info(
                "App commands in the testing guild have been cleared by %s (UserID: %s).",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply("App commands in the testing guild have been cleared.")

            self.is_clearing_testing = False

        else:
            logger.warning(
                "%s (UserID: %s) tried to clear app commands in the testing guild, however a local clearing process is already ongoing.",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply(
                "Bot is already in the process of clearing local app commands."
            )

    @sync_clear.command(
        name="global", extras={"required_user_permissions":["funtimes_bot_admin"]}
    )
    @is_bot_admin()
    async def sync_clear_global(self, ctx: commands.Context) -> None:
        """Remove all app commands globally and sync the bot."""

        if not self.is_clearing_global:
            self.is_clearing_global = True

            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync(guild=None)

            logger.info(
                "App commands have been globally cleared by %s (UserID: %s).",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply("App commands have been globally cleared.")

            self.is_clearing_global = False

        else:
            logger.warning(
                "%s (UserID: %s) tried to clear app commands globally, however a global clearing process is already ongoing.",
                ctx.author,
                ctx.author.id,
            )
            await ctx.reply(
                "Bot is already in the process of clearing global app commands."
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Sync(bot))

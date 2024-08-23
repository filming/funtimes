from discord.ext import commands

import logging

from utils.extension_paths import get_extension_paths
from utils.decorators.is_bot_admin import is_bot_admin

logger = logging.getLogger("discord")


class Reload(commands.Cog):
    """Cog for reloading extensions."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(extras={"required_user_permissions":["funtimes_bot_admin"]})
    @is_bot_admin()
    async def reload(self, ctx: commands.Context, extension: str = None) -> None:
        """Reload one or multiple extensions. Restricted to bot admins."""

        extension_paths = get_extension_paths()
        extensions_to_reload = []

        reloaded_extensions = set()
        loaded_extensions = set()

        if extension == None:
            # Set the specified extensions to be all the ones currently available
            extensions_to_reload = extension_paths

        else:
            # Find the specific extension(s)
            """
            We can even use this to reload specific dirs full of cogs based on what is sent in as the extension
            "admin" -> ['cogs.commands.admin.sync', 'cogs.commands.admin.reload', 'cogs.commands.admin.shutdown']
            "shutdown" -> ['cogs.commands.admin.shutdown']
            """
            for curr_extension_path in extension_paths:
                if extension.lower() in curr_extension_path:
                    extensions_to_reload.append(curr_extension_path)

        # Log and return early if no extension paths were found
        if not extensions_to_reload:
            logger.warning(
                "There was no extension(s) found with '%s' as a search parameter.",
                extension,
            )

            await ctx.send("**No extensions were reloaded/loaded.**")
            return

        # Reload the specified extensions
        for curr_extension in extensions_to_reload:
            try:
                await self.bot.reload_extension(curr_extension)
                reloaded_extensions.add(curr_extension)

                logger.info(
                    "Extension '%s' reloaded by %s (UserID: %s)",
                    curr_extension,
                    ctx.author,
                    ctx.author.id,
                )

            except commands.ExtensionNotLoaded:
                logger.warning(
                    "Extension '%s' wasn't reloaded as it hasn't been loaded yet.",
                    curr_extension,
                )

                try:
                    await self.bot.load_extension(curr_extension)
                    loaded_extensions.add(curr_extension)

                    logger.info(
                        "Extension '%s' loaded by %s (UserID: %s)",
                        curr_extension,
                        ctx.author,
                        ctx.author.id,
                    )

                except commands.NoEntryPointError as error:
                    logger.error(
                        "Extension '%s' has no setup function.",
                        curr_extension,
                        exc_info=error,
                    )

                except commands.ExtensionFailed as error:
                    error = getattr(error, "original", error)

                    logger.error(
                        "Extension '%s' was not reloaded due to the following error: %s",
                        curr_extension,
                        error,
                        exc_info=error,
                    )

        # Display output to user
        output_msg = ""

        if reloaded_extensions:
            reloaded_msg = "**Successfully reloaded the following extension(s):**\n"

            for curr_extension in reloaded_extensions:
                reloaded_msg += f"- {curr_extension}\n"

            output_msg += f"\n{reloaded_msg}"

        if loaded_extensions:
            loaded_msg = "**Successfully loaded the following extension(s):**\n"

            for curr_extension in loaded_extensions:
                loaded_msg += f"- {curr_extension}\n"

            output_msg += f"\n{loaded_msg}"

        await ctx.reply(output_msg)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reload(bot))

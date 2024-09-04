from dotenv import load_dotenv
import discord
from discord.ext import commands

import asyncio
import os
import json
import platform
import logging
from logging.handlers import TimedRotatingFileHandler
import zipfile
import time
import sqlite3

from utils.extension_paths import get_extension_paths


load_dotenv()

logger = logging.getLogger("discord")


class Config:
    """Class to hold all the bot variables and setup methods."""

    def __init__(self):
        self.dir_paths = {}

    def setup(self):
        """Run the basic setup flow for this class."""

        self.setup_storage()
        self.setup_logger()
        self.setup_env_vars()

    def setup_storage(self):
        """Setup the appropiate storage directories that the bot will need to use."""

        # Create storage directories if they don't already exist
        self.dir_paths["storage"] = os.path.join("..", "storage")
        self.dir_paths["logs"] = os.path.join(self.dir_paths["storage"], "logs")
        self.dir_paths["banners"] = os.path.join(self.dir_paths["storage"], "banners")

        for _, curr_path in self.dir_paths.items():
            os.makedirs(curr_path, exist_ok=True)

    def setup_logger(self):
        """Setup a TimedRotatingFileHandler that rotates at midnight and formats filenames dynamically."""

        # Configure formatter
        formatter = logging.Formatter(
            "[ %(asctime)s ] [ %(levelname)-8s] [ %(filename)-24s ] [ %(funcName)-24s ] :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Configure handler
        def rotator(source, dest):
            # Rotated log file is zipped and the original log file will be deleted
            zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED).write(
                source, os.path.basename(source)
            )
            os.remove(source)

        handler = TimedRotatingFileHandler(
            os.path.join(self.dir_paths["logs"], "current.log"),
            when="midnight",
            backupCount=365,
        )
        """
		default name for a log file that is being rotated (handler.namer lambda callable receives this):
		"current.log.2024-07-19"

		custom name for log file that is being rotated (lambda callable of handler.namer sets this):
		"2024-07-18.zip"
		"""
        handler.namer = lambda name: (
            os.path.join(self.dir_paths["logs"], f"{os.path.splitext(name)[1][1:]}.zip")
            if name.count(".") > 1
            else name
        )
        handler.rotator = rotator
        handler.setFormatter(formatter)

        # Configure logger
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

    def setup_env_vars(self):
        """Read values from the .env that are to be stored within the bot."""

        self.bot_user_groups = json.loads(os.getenv("BOT_USER_GROUPS"))
        self.testing_guild_id = os.getenv("TESTING_GUILD_ID")
        self.testing_guild = discord.Object(id=int(self.testing_guild_id))
        self.invite_link_guild = os.getenv("INVITE_LINK_GUILD")
        self.invite_link_bot = os.getenv("INVITE_LINK_BOT")


class MyClient(commands.Bot):
    """Class to be an extended version of commands.Bot.

    MyClient is a subclass of commands.Bot, allowing us to override setup_hook()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()
        self.platform = platform.system()

    def load_config(self):
        """Create a config obj that will store the bot variables."""

        config_obj = Config()
        config_obj.setup()

        self.config = config_obj

    def load_database(self):
        """Load an instance of a database into the bot."""

        DB_PATH = os.path.join(self.config.dir_paths["storage"], "funtimes.db")

        # Make sure DB instance exists
        if os.path.isfile(DB_PATH):
            logger.info("Existing database has been found.")
        else:
            logger.info("No database was found. A new one will be created.")

        db = sqlite3.connect(DB_PATH)

        # Create tables if they don't exist
        cursor = db.cursor()

        try:
            logger.info("Attempting to setup tables.")

            cursor.execute(
                """
				CREATE TABLE IF NOT EXISTS level (
					user_id BIGINT,
					guild_id BIGINT,
					experience INTEGER DEFAULT 0,
					level INTEGER DEFAULT 1,
                    previous_message_timestamp REAL DEFAULT 0,
					PRIMARY KEY (user_id, guild_id)
				)
				"""
            )
            logger.info("Level table has been setup.")

        except sqlite3.Error as e:
            logger.critical("Error creating table: %s", e)

        cursor.close()

        self.db = db

    async def load_extensions(self):
        """Load all of the initial extensions into the bot."""

        # Get all extension paths within the cogs directory
        extension_paths = get_extension_paths()

        # Load the initial extensions
        for extension in extension_paths:
            try:
                await self.load_extension(extension)

                logger.info("Initial extension loaded: %s", extension)

            except commands.NoEntryPointError as error:
                logger.error(
                    "Extension '%s' has no setup function.", extension, exc_info=error
                )

            except commands.ExtensionFailed as error:
                error = getattr(error, "original", error)

                logger.error(
                    "Extension '%s' was not loaded due to the following error: %s",
                    extension,
                    error,
                    exc_info=error,
                )

    async def setup_hook(self):
        """Run through the actions of setting up parts of the bot after login() has been called from start()."""

        self.load_config()
        logger.info("Config values have been loaded into the bot.")

        self.load_database()
        logger.info("Database has been setup.")

        await self.load_extensions()
        logger.info("Extensions have been loaded.")


# Setting intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Choose initial bot properties based on the current system-type
platform_system = platform.system()

if platform_system == "Linux":
    command_prefix = "$"
    activity = discord.Activity(
        type=discord.ActivityType.playing, name="Having FunTimes! | $help"
    )
    bot_token = os.getenv("BOT_TOKEN_MAIN")
else:
    command_prefix = "~"
    activity = discord.Activity(
        type=discord.ActivityType.playing, name="FunTimes | BETA"
    )
    bot_token = os.getenv("BOT_TOKEN_BETA")

# Create bot instance
bot = MyClient(
    command_prefix=command_prefix,
    activity=activity,
    intents=intents,
    case_insensitive=True,
)


async def main():
    """Start the bot"""

    async with bot:
        await bot.start(bot_token)


if __name__ == "__main__":
    asyncio.run(main())

import discord
from discord.ext import commands

import logging
import sqlite3
from typing import Dict

logger = logging.getLogger("discord")


class OnMessage(commands.Cog):
    """Cog for handling message events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def get_user_data(self, message: discord.Message) -> Dict[str, int]:
        """Return a dict representing the level table data of a user."""

        user_data = {
            "user_id": message.author.id,
            "guild_id": message.guild.id,
        }

        cur = self.bot.db.cursor()

        # Check if user exists in db, add them if not
        try:
            res = cur.execute(
                "SELECT * from level WHERE user_id = ? AND guild_id = ?",
                (message.author.id, message.guild.id),
            ).fetchone()

            if not res:
                # Add user to level table
                cur.execute(
                    "INSERT INTO level (user_id, guild_id) VALUES (?, ?)",
                    (message.author.id, message.guild.id),
                )
                self.bot.db.commit()

                logger.info(
                    "New user added to the level table. (userId: %s, guildId: %s)",
                    message.author.id,
                    message.guild.id,
                )

                user_data["experience"] = 0
                user_data["level"] = 0
                user_data["previous_message_timestamp"] = 0

            else:
                user_data["experience"] = res[2]
                user_data["level"] = res[3]
                user_data["previous_message_timestamp"] = res[4]

            cur.close()

        except sqlite3.Error as e:
            logger.error(f"Error fetching/adding user data: {e}")

        return user_data

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Process messages that are received through the bot."""

        # Only respond to messages from guilds
        if message.channel.type != "private":

            user_data = self.get_user_data(message)


# TODO: Implement XP gain, level-up logic, cooldown/rate limiting, etc.


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnMessage(bot))

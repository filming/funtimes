import discord
from discord.ext import commands

import logging
import time
import sqlite3
import random
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

    def update_user_experience(self, user_data, current_time):
        """Give a random amount of XP to a user."""

        # Only allow a user to get XP once every 25 secs
        if current_time - user_data["previous_message_timestamp"] >= 30:
            random_xp_amount = random.randint(15, 25)

            user_data["experience"] += random_xp_amount

        return user_data

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Process messages that are received through the bot."""
        current_time = time.time()

        # Only respond to messages from guilds
        if message.channel.type != "private":
            user_data = self.get_user_data(message)
            user_data = self.update_user_experience(user_data, current_time)


# TODO: Implement XP gain, level-up logic, cooldown/rate limiting, etc.


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnMessage(bot))

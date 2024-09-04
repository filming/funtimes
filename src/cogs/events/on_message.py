import discord
from discord.ext import commands

import logging
import time
import sqlite3
import random
from typing import Dict, Union

logger = logging.getLogger("discord")


class OnMessage(commands.Cog):
    """Cog for handling message events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def get_user_data(
        self, message: discord.Message
    ) -> Dict[str, Union[int, float]]:
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
                user_data["level"] = 1
                user_data["previous_message_timestamp"] = 0

            else:
                user_data["experience"] = res[2]
                user_data["level"] = res[3]
                user_data["previous_message_timestamp"] = res[4]

            cur.close()

        except sqlite3.Error as e:
            logger.error("Error fetching/adding user data: %s", e)

        return user_data

    async def update_user_experience(
        self, user_data: dict[str, Union[int, float]], current_time: float
    ) -> dict[str, Union[int, float]]:
        """Give a random amount of XP to a user."""

        # Only allow a user to get XP once every 30 secs
        if current_time - user_data["previous_message_timestamp"] >= 30:
            random_xp_amount = random.randint(15, 25)

            user_data["experience"] += random_xp_amount
            user_data["previous_message_timestamp"] = current_time

        return user_data

    async def update_user_level(
        self, message: discord.Message, user_data: dict[str, Union[int, float]]
    ) -> dict[str, Union[int, float]]:
        """Calculate and update the level of a user."""

        currently_stored_level = user_data["level"]
        calculated_level = int((user_data["experience"] // 62) ** 0.55) + 1

        if calculated_level > currently_stored_level:
            user_data["level"] = calculated_level

            if self.bot.platform == "Linux":
                await message.channel.send(
                    f"**{message.author.mention} Has Reached Level {calculated_level}!**"
                )

        return user_data

    async def update_database(self, user_data: dict[str, Union[int, float]]) -> None:
        """Store the updated user data object in the database."""

        cur = self.bot.db.cursor()

        try:
            cur.execute(
                "UPDATE level SET experience=?, level=?, previous_message_timestamp=? WHERE user_id=? AND guild_id=?",
                (
                    user_data["experience"],
                    user_data["level"],
                    user_data["previous_message_timestamp"],
                    user_data["user_id"],
                    user_data["guild_id"],
                ),
            )

            self.bot.db.commit()

        except sqlite3.Error as e:
            logger.error("Error fetching/adding user data: %s", e)

        cur.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Process messages that are received through the bot."""

        current_time = time.time()

        # Only respond to messages from guilds and non-bot users
        if (message.channel.type != "private") and (not message.author.bot):
            user_data = await self.get_user_data(message)
            user_data = await self.update_user_experience(user_data, current_time)
            user_data = await self.update_user_level(message, user_data)
            await self.update_database(user_data)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnMessage(bot))

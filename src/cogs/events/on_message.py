import discord
from discord.ext import commands

import logging

logger = logging.getLogger("discord")


class OnMessage(commands.Cog):
    """Cog for handling message events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Process messages that are received through the bot."""

        # Only respond to messages that are from guilds
        if message.channel.type != "private":
            cur = self.bot.db.cursor()

            # Add user to DB if they aren't already in it
            res = cur.execute(
                "SELECT * from level WHERE user_id = ? AND guild_id = ?",
                (message.author.id, message.guild.id),
            ).fetchone()

            if res == None:
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

            cur.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnMessage(bot))

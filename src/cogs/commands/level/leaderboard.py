import discord
from discord.ext import commands

from easy_pil import Canvas, Editor, Font, Text, load_image_async
from typing import Union

from random import randint
import logging
import sqlite3

logger = logging.getLogger("discord")


class Leaderboard(commands.Cog):
    """A cog that handles leaderboard related commands and methods."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx: commands.Context) -> None:
        """Display a leaderboard based on member ranks."""

        leaderboard_embed = discord.Embed(
            title=f"{ctx.guild.name}'s Level Leaderboard",
            colour=discord.Colour.from_str("#02f4fd"),
        )

        cur = self.bot.db.cursor()

        res = cur.execute(
            "SELECT user_id, experience, level FROM level WHERE guild_id=? ORDER BY experience DESC LIMIT 5",
            (ctx.guild.id,),
        ).fetchall()

        if len(res) == 5:
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅"]

            for i in range(5):
                leaderboard_embed.add_field(
                    name=f"{medals[i]} {await self.bot.fetch_user(res[i][0])}",
                    value=f"Level: {res[i][2]} ⚬ EXP: {res[i][1]}",
                    inline=False,
                )

            await ctx.reply(embed=leaderboard_embed)

        else:
            leaderboard_embed.description = (
                "**Not enough user data to create a leaderboard!**"
            )
            await ctx.reply(embed=leaderboard_embed)

        cur.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leaderboard(bot))

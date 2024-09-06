import discord
from discord.ext import commands

import logging

logger = logging.getLogger("discord")


class Leaderboard(commands.Cog):
    """A cog that handles leaderboard related commands and methods."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="leaderboard", aliases=["lb"])
    @commands.guild_only()
    async def leaderboard(self, ctx: commands.Context) -> None:
        """Display a leaderboard based on member ranks."""

        leaderboard_embed = discord.Embed(
            title=f"**{ctx.guild.name}'s Level Leaderboard**",
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

        else:
            leaderboard_embed.description = (
                "**Not enough user data to create a leaderboard!**"
            )

        await ctx.reply(embed=leaderboard_embed)

        cur.close()

    @commands.hybrid_command(name="server-position", aliases=["sp", "rp"])
    @commands.guild_only()
    async def server_position(self, ctx: commands.Context, position: int) -> None:
        """Display the member at a specific leaderboard rank position."""

        cur = self.bot.db.cursor()

        res = cur.execute(
            "SELECT user_id, experience, level FROM level WHERE guild_id=? ORDER BY experience DESC LIMIT ?",
            (ctx.guild.id, position),
        ).fetchall()

        server_position_embed = discord.Embed(colour=discord.Colour.from_str("#02f4fd"))

        if len(res) == position:
            user_data = {
                "user_id": res[-1][0],
                "experience": res[-1][1],
                "level": res[-1][2],
            }

            server_position_embed.title = f"**Level Stats for #{position}**"
            server_position_embed.description = (
                f"**User: {await self.bot.fetch_user(user_data['user_id'])}**"
            )

            server_position_embed.add_field(
                name="🏆 Server Rank", value=f"Rank Position: {position}", inline=False
            )
            server_position_embed.add_field(
                name="💯 Level & EXP",
                value=f"Level: {user_data['level']} ⚬ EXP: {user_data['experience']}",
                inline=False,
            )
            server_position_embed.add_field(
                name="⁉️ XP Until Level Up",
                value=f"Required XP: {abs(int(62 * ((user_data['level'] + 1) ** (20 / 11))) - user_data['experience'])}",
                inline=False,
            )

        else:
            server_position_embed.title = "**Rank**"
            server_position_embed.description = "**That rank position does not exist!**"

        await ctx.reply(embed=server_position_embed)

        cur.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leaderboard(bot))

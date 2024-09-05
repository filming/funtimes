import discord
from discord.ext import commands

from easy_pil import Canvas, Editor, Font, Text, load_image_async
from typing import Union


class Rank(commands.Cog):
    """A cog that handles rank related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rank", aliases=["level"])
    @commands.guild_only()
    async def rank(
        self, ctx: commands.Context, member: Union[discord.Member, None] = None
    ) -> None:
        """Display the level information of a guild member."""

        if not member:
            member = ctx.author

        cur = self.bot.db.cursor()

        res = cur.execute(
            "SELECT user_id, experience, level FROM level WHERE guild_id=? ORDER BY experience DESC",
            (ctx.guild.id,),
        ).fetchall()

        if len(res) > 0:
            member_found = False
            member_rank_position = 1
            member_level_obj = None

            rank_embed = discord.Embed(
                colour=discord.Colour.from_str("#02f4fd"),
            )

            for user in res:
                if user[0] == member.id:
                    member_found = True
                    member_level_obj = user
                    break
                else:
                    member_rank_position += 1

            if member_found:
                experience_for_next_level = round(
                    ((member_level_obj[2] + 1) ** (1 / 0.55)) * 62
                )

                user_data = {
                    "name": member.name,
                    "xp": member_level_obj[1],
                    "next_level_xp": experience_for_next_level,
                    "level": member_level_obj[2],
                    "percentage": (member_level_obj[1] / experience_for_next_level)
                    * 100,
                    "rank": member_rank_position,
                }

                background = Editor(Canvas((900, 300), color="#23272A"))
                profile_image = await load_image_async(member.display_avatar.url)
                profile = Editor(profile_image).resize((190, 190)).circle_image()

                poppins = Font.poppins(size=30)

                background.rectangle((20, 20), 894, 260, "#2a2e35")
                background.paste(profile, (50, 50))
                background.ellipse(
                    (42, 42), width=206, height=206, outline="#43b581", stroke_width=10
                )
                background.rectangle(
                    (260, 180), width=630, height=40, fill="#484b4e", radius=20
                )
                background.bar(
                    (260, 180),
                    max_width=630,
                    height=40,
                    percentage=user_data["percentage"],
                    fill="#00fa81",
                    radius=20,
                )
                background.text(
                    (270, 120), user_data["name"], font=poppins, color="#00fa81"
                )
                background.text(
                    (870, 125),
                    f"{user_data['xp']} / {user_data['next_level_xp']}",
                    font=poppins,
                    color="#00fa81",
                    align="right",
                )

                rank_level_texts = [
                    Text("Rank ", color="#00fa81", font=poppins),
                    Text(f"{user_data['rank']}", color="#1EAAFF", font=poppins),
                    Text("   Level ", color="#00fa81", font=poppins),
                    Text(f"{user_data['level']}", color="#1EAAFF", font=poppins),
                ]

                background.multi_text((850, 50), texts=rank_level_texts, align="right")

                file = discord.File(fp=background.image_bytes, filename="rank.png")
                await ctx.reply(file=file)

            else:
                rank_embed.description = "**This user does not have any level data!**"
                await ctx.reply(embed=rank_embed)

        else:
            rank_embed.description = "**This server does not have any level data!**"
            await ctx.reply(embed=rank_embed)

        cur.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Rank(bot))

import discord
from discord.ext import commands
from PIL import Image

from typing import *
from os import remove


class Banner(commands.Cog):
    """Cog for handling banner-related commands.

    This cog provides commands for users to view their own banners,
    as well as the banners of other users.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="banner")
    async def user_banner(
        self,
        ctx: commands.Context,
        user: Union[discord.Member, discord.User, None] = None,
    ) -> None:
        """Display a user's banner."""

        user = ctx.author if (not user) else user
        user = await self.bot.fetch_user(user.id)

        banner_embed = discord.Embed(
            colour=discord.Colour.from_str("#8308f7"),
            title="{}'s Banner".format(user),
        )

        banner_file = None

        if user.banner:
            banner_embed.set_image(url=user.banner)
        else:
            if user.accent_color:
                banner_img = Image.new("RGB", (256, 256), user.accent_colour.to_rgb())
                banner_img = banner_img.resize((400, 100))

                file_location = f"{self.bot.config.dir_paths['banners']}/{user.id}.jpg"

                banner_img.save(file_location)

                banner_file = discord.File(
                    file_location,
                    filename=f"{user.id}.jpg",
                )

                banner_embed.set_image(url=f"attachment://{user.id}.jpg")
                banner_embed.set_footer(text=f"Colour Code: {user.accent_colour}")

                remove(file_location)

            else:
                banner_embed.description = f"**This user has not setup a banner!**"

        await ctx.reply(embed=banner_embed, file=banner_file)

    @commands.hybrid_command(name="server-banner")
    async def server_banner(self, ctx: commands.Context) -> None:
        """Display this server's banner."""

        banner_embed = discord.Embed(
            colour=discord.Colour.from_str("#8308f7"),
            title="{}'s Banner".format(ctx.guild),
        )

        if ctx.guild.banner:
            banner_embed.set_image(url=ctx.guild.banner)
        else:
            banner_embed.description = "**This server has not setup a banner!**"

        await ctx.reply(embed=banner_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Banner(bot))

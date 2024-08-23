import discord
from discord.ext import commands

import logging

logger = logging.getLogger("discord")


class BotInvite(commands.Cog):
    """Cog to handle bot-specific invite commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="invite")
    async def invite_bot(self, ctx: commands.Context) -> None:
        """Provides a link to invite FunTimes to your own servers."""

        invite_bot_embed = discord.Embed(
            colour=discord.Colour.from_str("#8308f7"),
            title="🔗 __Invite FunTimes Bot__ 🔗",
            description=f"**▶️ [Click here to add FunTimes to your server!]({self.bot.config.invite_link_bot})**",
            url=self.bot.config.invite_link_bot,
        )
        invite_bot_embed.set_footer(text="Bring FunTimes features to your own servers!")

        await ctx.reply(embed=invite_bot_embed)

    @commands.hybrid_command(name="discord")
    async def invite_discord(self, ctx: commands.Context) -> None:
        """Provides an invite link to the official FunTimes Discord server."""

        invite_discord_embed = discord.Embed(
            colour=discord.Colour.from_str("#8308f7"),
            title="🔗 __Join FunTimes Discord Server__ 🔗",
            description=f"**▶️ [Click here to join the FunTimes discord!]({self.bot.config.invite_link_guild})**",
            url=self.bot.config.invite_link_guild,
        )
        invite_discord_embed.set_footer(
            text="Join our community for support and fun discussions!"
        )

        await ctx.reply(embed=invite_discord_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotInvite(bot))

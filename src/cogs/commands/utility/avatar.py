import discord
from discord.ext import commands

from typing import *

from utils.decorators.is_initial_interaction_author import is_initial_interaction_author


class Avatar(commands.Cog):
    """Cog for handling avatar-related commands.

    This cog provides commands for users to view their own avatars,
    as well as the avatars of other users.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="avatar", aliases=["av"])
    async def avatar(
        self,
        ctx: commands.Context,
        user: Union[discord.Member, discord.User, None] = None,
    ) -> None:
        """Display a user's profile picture."""

        user = ctx.author if (not user) else user

        # Member means that the user is in a guild, so they could have a guild pfp
        # User means that its just a general user, command could've been called in dms
        has_guild_avatar = False

        if isinstance(user, discord.Member):
            if user.guild_avatar:
                has_guild_avatar = True

        avatar_embeds = []

        if has_guild_avatar:
            guild_avatar_embed = discord.Embed(
                colour=discord.Colour.from_str("#8308f7"), title=f"{user.name}'s Avatar"
            )

            guild_avatar_embed.set_image(url=user.display_avatar.url)
            guild_avatar_embed.set_footer(text=f"∙ server avatar")

            avatar_embeds.append(guild_avatar_embed)

        global_avatar_embed = discord.Embed(
            colour=discord.Colour.from_str("#8308f7"), title=f"{user.name}'s Avatar"
        )
        global_avatar_embed.set_image(
            url=user.avatar.url if user.avatar else user.display_avatar.url
        )
        global_avatar_embed.set_footer(text=f"∙ global avatar")

        avatar_embeds.append(global_avatar_embed)

        if len(avatar_embeds) == 2:
            next_button_view = NextButtonView(user, avatar_embeds[1], None)
            back_button_view = BackButtonView(user, avatar_embeds[0], None)

            next_button_view.next_msg_view = back_button_view
            back_button_view.prev_msg_view = next_button_view

            await ctx.reply(embed=avatar_embeds[0], view=next_button_view)

        else:
            await ctx.reply(embed=avatar_embeds[0])


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Avatar(bot))


class NextButtonView(discord.ui.View):
    """A view with a next button.

    This is a subclass of discord.ui.View. It provides a next button that when
    pressed, allows the user to move to the next message state.
    """

    def __init__(
        self,
        initial_interaction_author: Union[discord.Member, discord.User],
        next_msg_embed: discord.Embed,
        next_msg_view: Union[discord.ui.View, None] = None,
    ) -> None:
        super().__init__(timeout=180)
        self.initial_interaction_author = initial_interaction_author
        self.next_msg_embed = next_msg_embed
        self.next_msg_view = next_msg_view

    @discord.ui.button(
        label="Next", emoji="➡️", style=discord.ButtonStyle.blurple, row=0
    )
    @is_initial_interaction_author
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.View
    ) -> None:
        """Handle the next button click event."""

        await interaction.response.defer()

        await interaction.message.edit(
            embed=self.next_msg_embed,
            view=self.next_msg_view,
        )


class BackButtonView(discord.ui.View):
    """A view with a back button.

    This is a subclass of discord.ui.View. It provides a back button that when
    pressed, allows the user to return to the previous message state.
    """

    def __init__(
        self,
        initial_interaction_author: Union[discord.Member, discord.User],
        prev_msg_embed: discord.Embed,
        prev_msg_view: Union[discord.ui.View, None] = None,
    ) -> None:
        super().__init__(timeout=180)
        self.initial_interaction_author = initial_interaction_author
        self.prev_msg_embed = prev_msg_embed
        self.prev_msg_view = prev_msg_view

    @discord.ui.button(
        label="Back", emoji="⬅️", style=discord.ButtonStyle.blurple, row=0
    )
    @is_initial_interaction_author
    async def back_button(
        self, interaction: discord.Interaction, button: discord.ui.View
    ) -> None:
        """Handle the back button click event."""

        await interaction.response.defer()

        await interaction.message.edit(
            embed=self.prev_msg_embed,
            view=self.prev_msg_view,
        )

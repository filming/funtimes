import discord
from discord.ext import commands

import logging
from typing import Dict

logger = logging.getLogger("discord")


class OnReaction(commands.Cog):
    """A cog that handles reaction events and related functions."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.cached = False
        self.funtimes_guild = None
        self.message_reactioners = {}
        self.tos = {}
        self.roles_channel = None

        # dicts are in a {emoji_id:role_id} format
        self.colour_emoji_dict = {
            906626424314675281: 856417327243722777,  # deep green
            906626424532795392: 856417327243722776,  # deep purple
            906626424549556355: 856417327243722775,  # strong fuchsia
            906626424562143272: 856417327243722774,  # deep magenta
            906626424549539870: 856417327243722773,  # vivid indigo
            906626424553746512: 856417327243722772,  # vivid blue
            906626424578908170: 856417327230877735,  # vivid amber
            906626424532766811: 856417327230877734,  # vivid raspberry
            906626424541163541: 856417327230877733,  # light magenta
            906626424574730260: 856417327230877732,  # pale purple
            906626424549556244: 856417327230877731,  # pale magenta
            906626424553758770: 856417327230877730,  # brilliant crimson
            906626424536989756: 856417327230877729,  # brilliant blue
            906626424293695549: 856417327230877728,  # brilliant gold
            906626424293699616: 856417327230877727,  # pale blue
            906626424562151505: 856417327230877726,  # sea green
            906626424536965150: 856417327208857640,  # cornflower blue
            906626424574738483: 856417327208857639,  # greenish white
            906626424629264404: 856417327208857638,  # pale yellow
            906626424293711883: 856417327208857637,  # vivid green
        }

        self.location_emoji_dict = {
            906641638418427914: 856417327208857636,  # africa
            906641638070321253: 856417327208857635,  # asia
            906641638435192872: 856417327208857634,  # europe
            906641638674284564: 856417327208857633,  # north america
            906641638653308978: 856417327208857632,  # south america
            906641638393257995: 856417327208857631,  # oceania
        }

        self.gender_emoji_dict = {
            906644266141491200: 856417327197192241,  # Female
            906644265793384540: 856417327197192240,  # Male
            906644265977921536: 856417327197192239,  # Other
        }

        self.age_emoji_dict = {
            906644284311236628: 856417327197192238,  # 13
            906644284030222357: 856417327197192237,  # 14
            906644284172816444: 856417327197192236,  # 15
            906644284210565180: 856417327197192235,  # 16
            906644284210544660: 856417327197192234,  # 17
            906644284286042112: 856417327197192233,  # 18+
        }

        # dict is in {message_id: {emoji_id: role_id}} format.
        self.message_to_emoji_dict = {
            906637057118580776: self.colour_emoji_dict,
            906637058976657508: self.location_emoji_dict,
            906637078060740668: self.gender_emoji_dict,
            906637079151251547: self.age_emoji_dict,
        }

    async def cache_funtimes_guild(self):
        """Cache data from the FunTimes guild."""

        # Cache the guild
        self.funtimes_guild = self.bot.get_guild(856417327175958528)

        # Cache the roles channel
        self.roles_channel = self.bot.get_channel(856417327376367619)

        # Cache the user's that have clicked on a reaction role
        # Storage foramt example: {color_msg_id: {color_emoji_id: {user1, user2, user3...}}}
        for message_id in self.message_to_emoji_dict:
            message = await self.roles_channel.fetch_message(message_id)

            self.message_reactioners[message_id] = {}

            for reaction in message.reactions:
                emoji_reactioners = set([user.id async for user in reaction.users()])

                self.message_reactioners[message_id][
                    reaction.emoji.id
                ] = emoji_reactioners

        # Cache the accept TOS message & role
        role = self.funtimes_guild.get_role(856417327188148252)
        self.tos["role"] = role

        self.cached = True

    async def manage_roles(
        self,
        member: discord.Member,
        message_id: int,
        emoji_id: int,
        emoji_role_dict: Dict[int, int],
    ):
        """Give a member a new role while removing all prior associated roles."""

        # Add new role to member
        role_to_add = self.funtimes_guild.get_role(emoji_role_dict[emoji_id])
        await member.add_roles(role_to_add)
        self.message_reactioners[message_id][emoji_id].add(member.id)

        # Remove any colour roles the member already had before prior to this new role
        curr_member_colour_roles = [
            role
            for role in member.roles
            if role.id in emoji_role_dict.values() and role.id != role_to_add.id
        ]
        await member.remove_roles(*curr_member_colour_roles)

        # Remove member from active list of members who selected a role (on prior roles)
        message = await self.roles_channel.fetch_message(message_id)

        for curr_emoji_id in self.message_reactioners[message_id]:
            curr_reaction = None

            for reaction in message.reactions:
                if reaction.emoji.id == curr_emoji_id:
                    curr_reaction = reaction
                    break

            if (curr_emoji_id != emoji_id) and (
                member.id in self.message_reactioners[message_id][curr_emoji_id]
            ):
                await curr_reaction.remove(member)

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        """Handle the event when a user reacts with a message."""

        if payload.guild_id == 856417327175958528:  # FunTimes Discord Server
            # Keep a copy of the funtimes guild & reactioners for quicker commands usages in the future
            if not self.cached:
                await self.cache_funtimes_guild()

            member = self.funtimes_guild.get_member(payload.user_id)

            # Handle member accepting TOS message
            if payload.message_id == 985917177850908742 and payload.emoji.name == "✅":
                await member.add_roles(self.tos["role"])

            # Handle member selecting a colour/location/gender/age role
            elif payload.message_id in self.message_to_emoji_dict:
                await self.manage_roles(
                    member,
                    payload.message_id,
                    payload.emoji.id,
                    self.message_to_emoji_dict[payload.message_id],
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Handle the event when a user removes a reaction from a message."""

        if payload.guild_id == 856417327175958528:  # FunTimes Discord Server
            # Keep a copy of the funtimes guild & reactioners for quicker commands usages in the future
            if not self.cached:
                await self.cache_funtimes_guild()

            member = self.funtimes_guild.get_member(payload.user_id)

            # Handle member accepting TOS message
            if payload.message_id == 985917177850908742 and payload.emoji.name == "✅":
                await member.add_roles(self.tos["role"])

            # Handle member selecting a colour/location/gender/age role
            elif payload.message_id in self.message_to_emoji_dict:
                role = self.funtimes_guild.get_role(
                    self.message_to_emoji_dict[payload.message_id][payload.emoji.id]
                )
                await member.remove_roles(role)
                self.message_reactioners[payload.message_id][payload.emoji.id].remove(
                    member.id
                )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OnReaction(bot))

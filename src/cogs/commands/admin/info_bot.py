import discord
from discord.ext import commands

import time
import platform
import psutil
import shutil
import cpuinfo
import subprocess

from utils.decorators.is_bot_admin import is_bot_admin


class InfoBot(commands.Cog):
    """Cog to handle commands regarding information about the bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def convert_seconds(self, seconds: int) -> str:
        """Convert an amount of a seconds into a time period string."""

        time_period_string = ""

        suffixes = {
            "year": 31540000,
            "month": 2628000,
            "week": 604800,
            "day": 86400,
            "hour": 3600,
            "minute": 60,
            "second": 1,
        }

        for time_period, time_period_in_sec in suffixes.items():

            if (seconds / time_period_in_sec) >= 1:
                time_period_string += f"{seconds // time_period_in_sec} {time_period}{'s' if (seconds / time_period_in_sec) >= 2 else ''}, "

                seconds -= time_period_in_sec * (seconds // time_period_in_sec)

        return time_period_string[:-2]

    def convert_percentage(
        self, percentage: int, active_symbol: str, inactive_symbol: str
    ) -> str:
        """Convert a percentage into an equivalent representative string of emojis."""

        active_symbol_count = min(100, percentage) // 10

        percentage_bar = [
            active_symbol if i <= (active_symbol_count - 1) else inactive_symbol
            for i in range(10)
        ]

        return "".join(percentage_bar)

    @commands.command(aliases=["info"])
    @is_bot_admin()
    async def info_bot(self, ctx: commands.Context) -> None:
        """Display important information about the bot."""

        bot_uptime = int(time.time() - self.bot.start_time)
        bot_uptime_str = self.convert_seconds(bot_uptime)
        app_info = await self.bot.application_info()

        # needed for operation system info
        platform_output = platform.system()

        # needed for cpu, ram & disk info
        cpu_usage_precent = abs(psutil.cpu_percent(interval=1))
        try:
            cpu_speed = (
                str(cpuinfo.get_cpu_info()["hz_advertised"][0] / 1000000000) + "GHz"
            )
        except:
            cpu_speed = "N/A"

        cpu_progressbar = self.convert_percentage(cpu_usage_precent, "🟥", "⬜")

        total_ram = abs(round(psutil.virtual_memory()[0] / 1000000000, 2))
        ram_available = abs(psutil.virtual_memory()[1] / 1000000000)
        ram_free = abs(psutil.virtual_memory()[4] / 1000000000)
        total_free_ram = abs(ram_available + ram_free)
        used_ram = abs(
            round((psutil.virtual_memory()[0] / 1000000000) - total_free_ram, 2)
        )
        used_ram_percent = abs(round((used_ram / (total_ram)) * 100, 2))
        ram_progressbar = self.convert_percentage(used_ram_percent, "🟦", "⬜")

        total, used, free = shutil.disk_usage("/")
        total_disk_formatted = abs(total // 2**30)
        used_disk_formatted = abs(used // 2**30)
        used_disk_percentage = abs(
            round((used_disk_formatted / total_disk_formatted) * 100, 2)
        )
        disk_progressbar = self.convert_percentage(used_disk_percentage, "🟩", "⬜")

        # needed for python & discord.py version info
        python_version = platform.python_version()

        installed_packages = subprocess.run(
            ["pip", "freeze"], capture_output=True, encoding="utf-8"
        ).stdout.split("\n")

        for curr_package in installed_packages:
            if curr_package:
                curr_package_name, curr_package_version = curr_package.split("==")

                if curr_package_name == "discord.py":
                    discord_version = curr_package_version

        # needed for getting number of commands
        app_commands_amount = len(self.bot.tree.get_commands())
        text_commands_amount = len(self.bot.commands)

        info_embed = discord.Embed(colour=discord.Colour.from_str("#c30008"))

        info_embed.add_field(
            name="<:DevBadge:978390859831717938> Developer",
            value=f"``` {app_info.owner} ({app_info.owner.id})```",
            inline=False,
        )
        info_embed.add_field(
            name="<:OnlineStatus:978390886234853378> Uptime",
            value=f"``` {bot_uptime_str} ```",
            inline=False,
        )
        info_embed.add_field(
            name="🌎 Guilds",
            value=f"``` {app_info.name} is in {len(self.bot.guilds)} guilds ```",
        )
        info_embed.add_field(
            name="📶 Ping",
            value=f"``` {round(self.bot.latency * 1000)}ms ```",
            inline=False,
        )
        info_embed.add_field(
            name="💻 Operating System", value=f"``` {platform_output} ```", inline=False
        )
        info_embed.add_field(
            name="⚙️ CPU Usage",
            value=f"``` {cpu_usage_precent}%\n Clock Speed: {cpu_speed} \n {cpu_progressbar} ```",
        )
        info_embed.add_field(
            name="⚙️ RAM Usage",
            value=f"``` {used_ram_percent}%\n {used_ram}GB / {total_ram}GB \n {ram_progressbar} ```",
        )
        info_embed.add_field(
            name="⚙️ Disk Usage",
            value=f"``` {used_disk_percentage}%\n {used_disk_formatted}GB / {total_disk_formatted}GB \n {disk_progressbar} ```",
            inline=False,
        )
        info_embed.add_field(
            name="<:python:979123559093903492> Python Version",
            value=f"``` {python_version} ```",
        )
        info_embed.add_field(
            name="<:discord_py:979123557898543134> Discord.py Version",
            value=f"``` {discord_version} ```",
        )
        info_embed.add_field(
            name="👑 Commands",
            value=f"``` # of App-Commands: {app_commands_amount} \n # of Text-Commands: {text_commands_amount} ```",
            inline=False,
        )

        await ctx.reply(embed=info_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InfoBot(bot))

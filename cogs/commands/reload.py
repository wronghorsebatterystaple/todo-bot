# super secret /reload command to reload extensions
# note: doesn't load in new/renamed cog files, or changes made in anywhere except /cogs

import os

from discord.ext import commands
from util.json_utils import *


async def setup(bot):
    await bot.add_cog(Reload(bot))


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #######################
    # /reload: reloads cogs
    @commands.command()
    async def reload(self, ctx:commands.Context):
        for file in os.listdir("./cogs/commands"):
            if file.endswith(".py"):
                await self.bot.reload_extension(f"cogs.commands.{file[:-3]}")
        for file in os.listdir("./cogs/taskloops"):
            if file.endswith(".py"):
                await self.bot.reload_extension(f"cogs.taskloops.{file[:-3]}")

        return

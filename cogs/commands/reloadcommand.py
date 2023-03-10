# super secret /reload command to reload extensions
# note: doesn't load in new/renamed cog files, or changes made in anywhere except /cogs

import os
from datetime import datetime

from discord.ext import commands
from util.json_utils import *


async def setup(bot):
    await bot.add_cog(ReloadCommand(bot))


class ReloadCommand(commands.Cog):
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


######################################################################################################################################################
#                                                              COMMAND PREFIX FUNCTIONS                                                              #
######################################################################################################################################################
# must do this for every file instead of having a master command group because command groups don't seem to carry between files


    ########################################################################################################################################
    # prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
    @reload.before_invoke
    async def disable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '\u0000'


    ########################
    # restore command prefix
    @reload.after_invoke
    async def enable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '/'

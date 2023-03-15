from discord.ext import commands
from util.command_utils import *


async def setup(bot):
    await bot.add_cog(Command(bot))


class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def editsubject(self, ctx:commands.Context, *args):
        pass


######################################################################################################################################################
#                                                        BEFORE/AFTER COMMAND INVOKE FUNCTIONS                                                       #
######################################################################################################################################################
# must do this for every file instead of having a master command group because command groups don't seem to carry between files


    ########################################################################################################################################
    # prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
    @editsubject.before_invoke
    async def disable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '\u0000'


    ########################
    # restore command prefix
    @editsubject.after_invoke
    async def enable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '/'
    

    ######################################################################################
    # make sure users have fully set their preferences before trying to do todo list stuff
    @editsubject.before_invoke
    async def check_prefs(self, ctx:commands.Context):
        await check_prefs_exist(ctx)
        
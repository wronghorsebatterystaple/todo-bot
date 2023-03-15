from discord.ext import commands
from util.command_utils import *


async def setup(bot):
    await bot.add_cog(Command(bot))


class Command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##################
    # /add: add a task
    @commands.command()
    async def add(self, ctx:commands.Context, *args):
        arg_length = len(args)

        # if an improper number of arguments is entered, return error
        if arg_length < 2:
            await ctx.send("> Too few arguments: the format is ```/add <subject> <task name> "\
                "<[optional] due date> <[optional] due time> <[optional] reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return
        if arg_length > 5:
            await ctx.send("> Too many arguments: the format is ```/add <subject> <task name> "\
                "<[optional] due date> <[optional] due time> <[optional] reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return


######################################################################################################################################################
#                                                        BEFORE/AFTER COMMAND INVOKE FUNCTIONS                                                       #
######################################################################################################################################################
# must do this for every file instead of having a master command group because command groups don't seem to carry between files


    ########################################################################################################################################
    # prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
    @add.before_invoke
    async def disable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '\u0000'


    ########################
    # restore command prefix
    @add.after_invoke
    async def enable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '/'
    

    ######################################################################################
    # make sure users have fully set their preferences before trying to do todo list stuff
    @add.before_invoke
    async def check_prefs(self, ctx:commands.Context):
        await check_prefs_exist(ctx)
        
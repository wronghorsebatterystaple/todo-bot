from discord.ext import commands

from util.command_utils import *


async def setup(bot):
    await bot.add_cog(Add(bot))


class Add(commands.Cog):
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

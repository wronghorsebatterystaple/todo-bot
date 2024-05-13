from discord.ext import commands

from util.command_utils import *


async def setup(bot):
    await bot.add_cog(EditSubject(bot))


class EditSubject(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def editsubject(self, ctx:commands.Context, *args):
        pass

from discord.ext import commands

from util.command_utils import *


async def setup(bot):
    await bot.add_cog(Syncdefaults(bot))


class Syncdefaults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def syncdefaults(self, ctx:commands.Context, *args):
        pass
        
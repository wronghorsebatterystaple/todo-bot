from discord.ext import commands

from util.command_utils import *


async def setup(bot):
    await bot.add_cog(Done(bot))


class Done(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def done(self, ctx:commands.Context, *args):
        pass

# /list
from discord.ext import commands


async def setup(bot):
    await bot.add_cog(ListCommand(bot))


class ListCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

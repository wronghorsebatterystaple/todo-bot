# /addsubject, /removesubject, /editsubject, /syncdefaults

from discord.ext import commands


async def setup(bot):
    await bot.add_cog(SubjectCommands(bot))


class SubjectCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
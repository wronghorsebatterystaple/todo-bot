# /add, /remove, /edit, /done, /notdone


from discord.ext import commands


async def setup(bot):
    await bot.add_cog(TaskCommands(bot))


class TaskCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

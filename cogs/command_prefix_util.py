from discord.ext import commands


async def setup(bot):
    await bot.add_cog(CommandPrefixUtil(bot))

class CommandPrefixUtil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

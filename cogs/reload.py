# secret /reload command to reload extensions
# note: doesn't load in new/renamed cog files

import os

from discord.ext import commands


async def setup(bot):
    await bot.add_cog(Reload(bot))


class Reload(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx:commands.Context):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.bot.reload_extension(f"cogs.{file[:-3]}")

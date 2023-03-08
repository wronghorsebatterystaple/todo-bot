import os
from datetime import time

from discord.ext import commands, tasks
from util.json_utils import *
from util.time_utils import *


times = []

async def setup(bot):
    await bot.add_cog(TickedItemDeletionLoop())

class TickedItemDeletionLoop(commands.Cog):
    def __init__(self):
        self.update()


    def update(self):
        # set time = times where times is a list of midnight in utc + all the user diffs
        for file in os.listdir("./jsons/preferences"):
            pass


    # @tasks.loop(time=times)
    # async def check_ticked_item_deletion(self):
    #     pass
    # match current time to each timezone in user caches to check which is the current user(s) that needs to be checked
    # check if time since last deletion in that user's cache
        # if time matches preferences, check for ticks in that user's todolist and delete
        # then update that user's cache
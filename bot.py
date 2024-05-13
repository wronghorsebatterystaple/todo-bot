import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

from util.json_utils import *


######################################################################################################################################################
#                                                                     BOT INIT                                                                       #
######################################################################################################################################################


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # save token to gitignored .env file


# initialize bot using discord.ext's commands.Bot instead of discord.py's discord.Client for simpler management of cogs (commands)
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())


@bot.event
async def on_ready():
    # initialize and load cogs
    for file in os.listdir("./cogs/commands"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.commands.{file[:-3]}")
    for file in os.listdir("./cogs/taskloops"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.taskloops.{file[:-3]}")


######################################################################################################################################################
#                                                                    BOT EVENTS                                                                      #
######################################################################################################################################################


########################
# catch invalid commands
@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("what\n\nYou have entered an invalid command, ping me for help.")


########################################################################################################################################
# prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
# and also prevent users from doing todo list stuff before fully setting up their preferences
@bot.event
async def on_command(ctx:commands.Context):
    bot.command_prefix = '\u0000'

    command_name = ctx.command.name
    if command_name != "pref" and command_name != "show" and command_name != "change":
        author = ctx.author
        if not os.path.isfile(f"./jsons/preferences/{author}.json"):
            await ctx.send("> Please run ```/pref change all``` to set up preferences first.")
        elif len(read_json("preferences", author).items()) < 12:
            await ctx.send("> Please run ```/pref change all``` to set up all preferences first.")


###############################################
# reset command prefix after command completion
@bot.event
async def on_command_completion(ctx:commands.Context):
    bot.command_prefix = '/'


######################################################################################################################################################
#                                                                      BOT RUN                                                                       #
######################################################################################################################################################


bot.run(TOKEN)

import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # save token to gitignored .env file

# initialize bot using disord.ext's commands.Bot instead of discord.py's discord.Client for simpler management of cogs (commands)
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())


# catch invalid commands
@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("what\n\nYou have entered an invalid command, ping me for help.")


@bot.event
async def on_ready():
    # initialize and load cogs
    for file in os.listdir("./cogs/commands"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.commands.{file[:-3]}")
    for file in os.listdir("./cogs/taskloops"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.taskloops.{file[:-3]}")


bot.run(TOKEN)

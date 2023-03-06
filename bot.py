import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound

# temp https://stackoverflow.com/questions/67295010/how-do-i-schedule-a-task-to-run-at-a-fixed-time-in-discord-py, https://www.javaer101.com/en/article/40873438.html

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # save token to gitignored .env file

# initialize bot using disord.ext's commands.Bot instead of discord.py's discord.Client for simpler management of cogs (commands)
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    # initialize and load command cogs
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

# catch invalid commands
@bot.event
async def on_command_error(ctx:commands.Context, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("what\n\nYou have entered an invalid command, ping me for help.")

bot.run(TOKEN)

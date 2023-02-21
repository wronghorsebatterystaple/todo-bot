import os
import json

from discord.ext import commands


async def setup(bot):
    await bot.add_cog(Prefs(bot))


class Prefs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefs = {} # dictionary to read and write user preferences to json


######################################################################################################################################################
######################################################################################################################################################


    # /pref: changes specific preference or show all of them
    @commands.command()
    async def pref(self, ctx:commands.Context, arg1=""):
        author = ctx.message.author
        # super non-expandable method of storing user preferences as local json files, but I'm not planning to expand this widely anyways
        # read preferences from json
        self.prefs = self.read_JSON(author)

        # if /pref is used with no arguments, show list of all existing preferences
        if arg1 == "":
            output_message = "These are your currently set preferences:"
            # reply in a more readable format than json
            for k, v in self.prefs.items():
                output_message += "\n\t"
                k = " ".join(k.split("_")) # replace underscores with spaces
                output_message += k
                output_message += ": "
                output_message += v
            await ctx.send(output_message)
            return
        
        # else parse argument to match with preference number/name        
        if arg1[0].isdigit(): # if the argument starts with/is a number, try to match with existing preference number from json
            await self.choose_pref_num(ctx, author, arg1)
            return
        
        # else match with the first preference in order of their numerical label that completely matches the argument
        await self.choose_pref_name(ctx, author, arg1)
        return
    

######################################################################################################################################################
######################################################################################################################################################


    # /allprefs: changes all preferences
    @commands.command()
    async def allprefs(self, ctx:commands.Context):
        author = ctx.message.author
        # read preferences from json
        self.prefs = self.read_JSON(author)

        await self.dow_or_date(ctx, author)
        await self.date_format(ctx, author)
    
######################################################################################################################################################
######################################################################################################################################################
    

    # helper function to match arguments to preferences in /pref based on their numerical labels
    async def choose_pref_num(self, ctx:commands.Context, author, arg1):
        item_counter = 0 # to keep track of the actual numerical label of the arguments
        
        for k in self.prefs.keys():
            item_counter += 1
            if k[0] == arg1[0]: # if match found
                match item_counter:
                    case 1:
                        await self.dow_or_date(ctx, author)
                        await ctx.send("Preference for \"DOW or date\" changed to: " + self.prefs["1. DOW_or_date"])
                        return
                    case 2:
                        await self.date_format(ctx, author)
                        await ctx.send("Preference for \"date format\" changed to: " + self.prefs["2. Date_format"])
                        return
                    case _:
                        await ctx.send("how did we get here?") # you should never be here
                        return
        
        # else if match not found because of invalid argument
        await ctx.send("what")


    # helper function to match arguments to preferences in /pref based on their names
    async def choose_pref_name(self, ctx:commands.Context, author, arg1):
        arg_length = len(arg1)
        arg1 = arg1.lower()
        item_counter = 0

        for k in self.prefs.keys():
            item_counter += 1
            if len(k) < (arg_length - 3): # if argument is longer than the preference name
                continue
            if arg1 == (k[3:3 + arg_length]).lower(): # else if match found
                match item_counter:
                    case 1:
                        await self.dow_or_date(ctx, author)
                        await ctx.send("Preference for \"DOW or date\" changed to: " + self.prefs["1. DOW_or_date"])
                        return
                    case 2:
                        await self.date_format(ctx, author)
                        await ctx.send("Preference for \"date format\" changed to: " + self.prefs["2. Date_format"])
                        return
                    case _:
                        await ctx.send("how did we get here?")
                        return
        
        # else if match not found because of invalid argument
        await ctx.send("what")


    # helper function for setting DOW or date preference
    async def dow_or_date(self, ctx:commands.Context, author):
        await ctx.send("1. DOW or date\n\t→ Enter \"DOW\" if you would like to have dates represented by days of the week, otherwise enter \"date\".")

        def check_response(message):
            message = (str(message.content)).lower()
            return message == "dow" or message == "date"
            
        response = await self.bot.wait_for("message", check=check_response)
        response = str(response.content)
        response = response.lower() if response.lower() == "date" else response.upper() # capitalize DOW
        self.prefs["1. DOW_or_date"] = response
        
        # write updated preferences into json every time in case allprefs sequence is cut off for whatever reason
        self.write_JSON(author)
    

    # helper function for setting date format preference
    async def date_format(self, ctx:commands.Context, author):
        await ctx.send("2. Date format\n\t→ Enter \"YYYY-MM-DD\", \"MM-DD-YYYY\", or \"DD-MM-YYYY\", even if you've chosen DOW over dates")

        def check_response(message):
            message = (str(message.content)).upper()
            return message == "YYYY-MM-DD" or message == "MM-DD-YYYY" or message == "DD-MM-YYYY"
        
        response = await self.bot.wait_for("message", check=check_response)
        response = str(response.content).upper()
        self.prefs["2. Date_format"] = response
        self.write_JSON(author)


    def read_JSON(self, author):
        filepath = f"cogs/jsons/{author}.json"
        if os.path.isfile(filepath) and os.stat(filepath).st_size > 0: # if file exists and is not empty
            with open(filepath, "r") as infile: # read from file
                return json.load(infile)
        else:
            open(filepath, "a+") # a+ mode creates the file if it doesn't exist
            return dict()
        
        
    def write_JSON(self, author):
        with open(f"cogs/jsons/{author}.json", "w+") as outfile:
            json.dump(self.prefs, outfile, indent=2)

from discord.ext import commands
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(PrefCommands(bot))


class PrefCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefs = {} # dictionary to read and write user preferences to json


######################################################################################################################################################
#                                                                      COMMANDS                                                                      #
######################################################################################################################################################


    ########################################################
    # /pref: changes specific preference or show all of them
    @commands.command()
    async def pref(self, ctx:commands.Context, arg1=""):

        # read preferences from json
        author = ctx.message.author
        self.prefs = read_JSON(author)

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
        # if the argument starts with/is a number, try to match with existing preference number from json
        if arg1[0].isdigit():
            await self.choose_pref_num(ctx, author, arg1)
            return
            
        # else match with the first preference in order of their numerical label that completely matches the argument
        await self.choose_pref_name(ctx, author, arg1)
        return
    

    ####################################
    # /allprefs: changes all preferences
    @commands.command()
    async def allprefs(self, ctx:commands.Context):
        # read preferences from json
        author = ctx.message.author
        self.prefs = read_JSON(author)

        # call every preference-setting function
        await self.set_dow_or_date(ctx, author)
        await self.set_date_format(ctx, author)
        await self.set_time_format(ctx, author)
        await self.set_start_of_weeks(ctx, author)
        await self.set_default_due_time(ctx, author)
        await self.set_default_reminder_timing(ctx, author)

        return
    
    
######################################################################################################################################################
#                                                            PREFERENCE-SETTING FUNCTIONS                                                            #
######################################################################################################################################################


    ################################################
    # 1. function for setting DOW or date preference
    async def set_dow_or_date(self, ctx:commands.Context, author):
        await ctx.send("1. DOW or date\n\t→ Enter \"DOW\" if you would like to have dates represented by days of the week, otherwise enter \"date\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "dow" or message_str == "date"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content)
        response = response.lower() if response.lower() == "date" else response.upper() # capitalize DOW
        self.prefs["1. DOW_or_date"] = response
        write_JSON(author, self.prefs) # write updated preferences into json every time in case allprefs sequence is cut off for whatever reason
        # print confirmation
        await ctx.send("> Preference for \"DOW or date\" set to: " + self.prefs["1. DOW_or_date"])
        return
    

    ################################################
    # 2. function for setting date format preference
    async def set_date_format(self, ctx:commands.Context, author):
        await ctx.send("2. Date format\n\t→ Enter \"YYYY-MM-DD\", \"MM-DD-YYYY\", or \"DD-MM-YYYY\", even if you've chosen DOW instead of dates")

        def check_response(message):
            message_str = (str(message.content)).upper()
            return message_str == "YYYY-MM-DD" or message_str == "MM-DD-YYYY" or message_str == "DD-MM-YYYY"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        response = str(response.content).upper()
        # save response to user preferences
        self.prefs["2. Date_format"] = response
        write_JSON(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"date format\" set to: " + self.prefs["2. Date_format"])
        return


    ################################################
    # 3. function for setting time format preference
    async def set_time_format(self, ctx:commands.Context, author):
        await ctx.send("3. Time Format\n\t→ Enter \"12\" or \"24\" for 12-hour or 24-hour time respectively")

        def check_response(message):
            message_str = str(message.content)
            return message_str == "12" or message_str == "24"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        self.prefs["3. Time_format"] = str(response.content) + "-hour"
        write_JSON(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"time format\" set to: " + self.prefs["3. Time_format"])
        return

    
    ##################################################
    # 4. function for setting start of week preference
    async def set_start_of_weeks(self, ctx:commands.Context, author):
        await ctx.send("4. Start of week\n\t→ Enter \"sun\" or \"mon\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "sun" or message_str == "mon"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).capitalize()
        self.prefs["4. Start_of_week"] = response
        write_JSON(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"start of week\" set to: " + self.prefs["4. Start_of_week"])
        return
    

    ##########################################
    # 5. function for setting default due time
    async def set_default_due_time(self, ctx:commands.Context, author):
        await ctx.send("5. Default due time\n\t→ Enter a time in either 12- or 24-hour format w/o seconds, e.g. \"1159 pm\" or \"23:59\"")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed timestr from the checking function
            response = await self.bot.wait_for("message")
            response = time_to_timestr(str(response.content).lower())
            valid = response != "error"
        # save response to user preferences json
        response = timestr_to_displaystr(response, self.prefs)
        self.prefs["5. Default_due_time"] = response
        write_JSON(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"default due time\" set to: " + self.prefs["5. Default_due_time"])
        return
    

    #################################################
    # 6. function for setting default reminder timing
    async def set_default_reminder_timing(self, ctx:commands.Context, author):
        await ctx.send("6. Default reminder timing\n\t→ Enter a duration w/o seconds for the amount of time before due to send a reminder, e.g. \"2:00\" or \"0:45\"")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed durstr from the checking function
            response = await self.bot.wait_for("message")
            response = dur_to_durstr(str(response.content))
            valid = response != "error"
        # save response to user preferences json
        response = durstr_to_displaystr(response)
        self.prefs["6. Default_reminder_timing"] = response
        write_JSON(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"default reminder timing\" set to: " + self.prefs["6. Default_reminder_timing"])
        return
    
    
######################################################################################################################################################
#                                                                  HELPER FUNCTIONS                                                                  #
######################################################################################################################################################


    ##########################################################################################
    # match arguments in /pref to preference-setting functions based on their numerical labels
    async def choose_pref_num(self, ctx:commands.Context, author, arg1):
        item_counter = 0 # to keep track of the actual numerical label of the arguments
        
        for k in self.prefs.keys():
            item_counter += 1
            if k[0] == arg1[0]: # if match found
                match item_counter:
                    case 1:
                        await self.set_dow_or_date(ctx, author)
                        return
                    case 2:
                        await self.set_date_format(ctx, author)
                        return
                    case 3:
                        await self.set_time_format(ctx, author)
                        return
                    case 4:
                        await self.set_start_of_weeks(ctx, author)
                        return
                    case 5:
                        await self.set_default_due_time(ctx, author)
                        return
                    case 6:
                        await self.set_default_reminder_timing(ctx, author)
                        return
        
        # else if match not found because of invalid argument
        await ctx.send("what")
        return


    ###############################################################################
    # match arguments in /pref to preference-setting functions based on their names
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
                        await self.set_dow_or_date(ctx, author)
                        return
                    case 2:
                        await self.set_date_format(ctx, author)
                        return
                    case 3:
                        await self.set_time_format(ctx, author)
                        return
                    case 4:
                        await self.set_start_of_weeks(ctx, author)
                        return
                    case 5:
                        await self.set_default_due_time(ctx, author)
                        return
                    case 6:
                        await self.set_default_reminder_timing(ctx, author)
                        return
        
        # else if match not found because of invalid argument
        await ctx.send("what")
        return


######################################################################################################################################################
#                                                              COMMAND PREFIX FUNCTIONS                                                              #
######################################################################################################################################################
# must do this for every file instead of having a master command group because command groups don't seem to carry between files


    ########################################################################################################################################
    # prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
    @pref.before_invoke
    @allprefs.before_invoke
    async def disable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '\u0000'


    ########################
    # restore command prefix
    @pref.after_invoke
    @allprefs.after_invoke
    async def enable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '/'

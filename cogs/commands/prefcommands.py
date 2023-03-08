from datetime import datetime

from discord.ext import commands
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(PrefCommands(bot))


class PrefCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefs = {} # dictionary to read and write command caller's preferences to json


######################################################################################################################################################
#                                                                      COMMANDS                                                                      #
######################################################################################################################################################


    ########################################################
    # /pref: changes specific preference or show all of them
    @commands.command()
    async def pref(self, ctx:commands.Context, *, arg1=""): # asterisk is "consume rest" which allows multiple-word arguments
        # read preferences from json
        author = ctx.message.author
        self.prefs = read_json("preferences", author)

        # if /pref is used with no arguments, show list of all existing preferences
        if arg1 == "":
            output_message = "These are your currently set preferences:"
            # reply in a more readable format than json
            for k, v in self.prefs.items():
                if not isinstance(v, dict):
                    output_message += "\n\t"
                    k = ' '.join(k.split('_')) # replace underscores with spaces
                    output_message += k
                    output_message += ": "
                    output_message += v
                # if single-nested json entry, unpack the nested dictionary too
                else:
                    output_message += "\n\t"
                    k = ' '.join(k.split('_')) # replace underscores with spaces
                    output_message += k
                    for kk, vv in v.items():
                        output_message += "\n\t\t"
                        kk = ' '.join(kk.split('_')) # replace underscores with spaces
                        output_message += kk
                        output_message += ": "
                        output_message += vv
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
        self.prefs = read_json("preferences", author)

        # call every preference-setting function
        await self.set_timezone(ctx, author)
        await self.set_dow_or_date(ctx, author)
        await self.set_date_format(ctx, author)
        await self.set_time_format(ctx, author)
        await self.set_start_of_weeks(ctx, author)
        await self.set_default_due_time(ctx, author)
        await self.set_default_reminder_timing(ctx, author)
        await self.set_completion_ticks(ctx, author)

        return
    
    
######################################################################################################################################################
#                                                            PREFERENCE-SETTING FUNCTIONS                                                            #
######################################################################################################################################################


    ################################################
    # 1. function for setting DOW or date preference
    async def set_timezone(self, ctx:commands.Context, author):
        await ctx.send("1. Timezone\n\t→ Enter your timezone, e.g. \"-8:00\", \"14:00\", or \"+00:00\".")
    
        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed timestr from the checking function
            response = await self.bot.wait_for("message")
            response = tz_to_tzstr(str(response.content).lower())
            valid = response != "error"
        # save response to user preferences json
        response = tzstr_to_displaystr(response)
        self.prefs["1. Timezone"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"timezone\" set to: " + self.prefs["1. Timezone"])
        return
    
    
    ################################################
    # 2. function for setting DOW or date preference
    async def set_dow_or_date(self, ctx:commands.Context, author):
        await ctx.send("2. DOW or date\n\t→ Enter \"DOW\" if you would like to have dates represented by days of the week, otherwise enter \"date\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "dow" or message_str == "date"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content)
        response = response.lower() if response.lower() == "date" else response.upper() # capitalize DOW
        self.prefs["2. DOW_or_date"] = response
        write_json("preferences", author, self.prefs) # write updated preferences into json every time in case allprefs sequence is cut off for whatever reason
        # print confirmation
        await ctx.send("> Preference for \"DOW or date\" set to: " + self.prefs["2. DOW_or_date"])
        return
    

    ################################################
    # 3. function for setting date format preference
    async def set_date_format(self, ctx:commands.Context, author):
        await ctx.send("3. Date format\n\t→ Enter \"YYYY-MM-DD\", \"MM-DD-YYYY\", or \"DD-MM-YYYY\", even if you've chosen DOW instead of dates")

        def check_response(message):
            message_str = (str(message.content)).upper()
            return message_str == "YYYY-MM-DD" or message_str == "MM-DD-YYYY" or message_str == "DD-MM-YYYY"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        response = str(response.content).upper()
        # save response to user preferences
        self.prefs["3. Date_format"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"date format\" set to: " + self.prefs["3. Date_format"])
        return


    ################################################
    # 4. function for setting time format preference
    async def set_time_format(self, ctx:commands.Context, author):
        await ctx.send("4. Time Format\n\t→ Enter \"12\" or \"24\" for 12-hour or 24-hour time respectively")

        def check_response(message):
            message_str = str(message.content)
            return message_str == "12" or message_str == "24"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        self.prefs["4. Time_format"] = str(response.content) + "-hour"
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"time format\" set to: " + self.prefs["4. Time_format"])
        return

    
    ##################################################
    # 5. function for setting start of week preference
    async def set_start_of_weeks(self, ctx:commands.Context, author):
        await ctx.send("5. Start of week\n\t→ Enter \"sun\" or \"mon\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "sun" or message_str == "mon"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).capitalize()
        self.prefs["5. Start_of_week"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"start of week\" set to: " + self.prefs["5. Start_of_week"])
        return
    

    ##########################################
    # 6. function for setting default due time
    async def set_default_due_time(self, ctx:commands.Context, author):
        await ctx.send("6. Default due time\n\t→ Enter a time in either 12- or 24-hour format w/o seconds, e.g. \"1159 pm\" or \"23:59\"")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed timestr from the checking function
            response = await self.bot.wait_for("message")
            response = time_to_timestr(str(response.content).lower())
            valid = response != "error"
        # save response to user preferences json
        response = timestr_to_displaystr(response, self.prefs)
        self.prefs["6. Default_due_time"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"default due time\" set to: " + self.prefs["6. Default_due_time"])
        return
    

    #################################################
    # 7. function for setting default reminder timing
    async def set_default_reminder_timing(self, ctx:commands.Context, author):
        await ctx.send("7. Default reminder timing\n\t→ Enter a duration w/o seconds for the amount of time before a due date to send a reminder, e.g. \"2:00\" or \"0:45\". \"00:00\" means no reminders.")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed durstr from the checking function
            response = await self.bot.wait_for("message")
            response = dur_to_durstr(str(response.content))
            valid = response != "error"
        # save response to user preferences json
        response = durstr_to_displaystr(response)
        self.prefs["7. Default_reminder_timing"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"default reminder timing\" set to: " + self.prefs["7. Default_reminder_timing"])
        return
    

    ##########################################
    # 8a. function for setting completion ticks
    async def set_completion_ticks(self, ctx:commands.Context, author):
        await ctx.send("8a. Completion Ticks\n\t→ Enter \"yes\" if you want completed items to be ticked rather than immediately removed, otherwise enter \"no\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).lower()
        self.prefs["8. Completion_ticks"] = {"8a. Exists": response}
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"completion ticks\" set to: " + self.prefs["8. Completion_ticks"]["8a. Exists"])

        # follow-ups if "yes"
        if response == "yes":
            await self.set_tick_colors(ctx, author)
            await self.set_days_per_deletion_of_ticked_items(ctx, author)
        return
    

    #######################################
    # 8b. function for setting tick colors
    async def set_tick_colors(self, ctx:commands.Context, author):
        await ctx.send("8b. Tick Colors\n\t→ Enter \"yes\" if you want ticks to be colored by day of week completed, otherwise enter \"no\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json as nested dictionary
        response = str(response.content).lower()
        self.prefs["8. Completion_ticks"]["8b. Colors"] = response
        write_json("preferences", author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"tick colors\" set to: " + self.prefs["8. Completion_ticks"]["8b. Colors"])
        return
    

    ###################################################################
    # 8c. function for setting days per check for deleting ticked items
    async def set_days_per_deletion_of_ticked_items(self, ctx:commands.Context, author):
        await ctx.send("8c. Days Per Deletion of Ticked Items\n\t→ Enter the number of days between each check to clear ticked items; e.g. 6 means clear once every 6 days starting the most recent " + self.prefs["4. Start_of_week"])

        def check_response(message):
            message_str = (str(message.content)).lower()
            if message_str.isnumeric():
                if int(message_str) > 0:
                    return True
            return False
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json as nested dictionary
        response = str(response.content)
        self.prefs["8. Completion_ticks"]["8c. Days_per_deletion_of_ticked"] = response
        write_json(author, self.prefs)
        # print confirmation
        await ctx.send("> Preference for \"days per deletion of ticked items\" set to: " + self.prefs["8. Completion_ticks"]["8c. Days_per_deletion_of_ticked"])
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
                        await self.set_timezone(ctx, author)
                        return
                    case 2:
                        await self.set_dow_or_date(ctx, author)
                        return
                    case 3:
                        await self.set_date_format(ctx, author)
                        return
                    case 4:
                        await self.set_time_format(ctx, author)
                        return
                    case 5:
                        await self.set_start_of_weeks(ctx, author)
                        return
                    case 6:
                        await self.set_default_due_time(ctx, author)
                        return
                    case 7:
                        await self.set_default_reminder_timing(ctx, author)
                        return
                    case 8:
                        await self.set_completion_ticks(ctx, author)
                        return
        
        # else if match not found because of invalid argument
        await ctx.send("what")
        return


    ###############################################################################
    # match arguments in /pref to preference-setting functions based on their names
    async def choose_pref_name(self, ctx:commands.Context, author, arg1):
        arg_length = len(arg1)
        arg1 = arg1.lower()
        arg1 = '_'.join(arg1.split(' ')) # replace spaces with underscores since json uses underscores
        item_counter = 0

        for k in self.prefs.keys():
            item_counter += 1
            if len(k) < (arg_length - 3): # if argument is longer than the preference name
                continue
            if arg1 == (k[3:3 + arg_length]).lower(): # else if match found
                match item_counter:
                    case 1:
                        await self.set_timezone(ctx, author)
                        return
                    case 2:
                        await self.set_dow_or_date(ctx, author)
                        return
                    case 3:
                        await self.set_date_format(ctx, author)
                        return
                    case 4:
                        await self.set_time_format(ctx, author)
                        return
                    case 5:
                        await self.set_start_of_weeks(ctx, author)
                        return
                    case 6:
                        await self.set_default_due_time(ctx, author)
                        return
                    case 7:
                        await self.set_default_reminder_timing(ctx, author)
                        return
                    case 8:
                        await self.set_completion_ticks(ctx, author)
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


    # #################################################################################
    # # cache/update time offset of command caller from bot, useful for taskloop checks
    # @pref.before_invoke
    # @allprefs.before_invoke
    # async def get_timezones(self, ctx:commands.Context):
    #     # get bot's UTC offset in minutes
    #     offset = datetime.now() - datetime.utcnow() # datetime.timedelta object
    #     bot_UTC_offset = offset.days * 1440 + offset.seconds // 60

        

    #     # # get user's timezone offset from the bot in minutes and write to user's cache
    #     # author = ctx.author
    #     # usercache = read_json("usercache", author)
    #     # usercache["Time_offset_from_bot_mins"] = user_UTC_offset - bot_UTC_offset
    #     # write_json("usercache", author, usercache)
        
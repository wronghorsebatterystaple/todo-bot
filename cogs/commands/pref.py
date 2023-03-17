from functools import partial

from discord.ext import commands

from util.command_utils import *
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(Pref(bot))

class Pref(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.preferences = {} # dictionary to read and write command caller's preferences to json


######################################################################################################################################################
#                                                                      COMMAND                                                                       #
######################################################################################################################################################


    #####################################
    # /pref: show or change preference(s)
    @commands.group(name="pref", invoke_without_command=True) # invoke_without_command=False allows before_invoke and after_invoke functions to run
    async def pref(self, ctx:commands.Context):
        await ctx.send("> Use ```/pref show <\"all\"/pref number/pref name>``` to show prefs and ```/pref change <\"all\"/pref number/pref name>``` to change prefs.")
        return

    
    ################################
    # /pref show: show preference(s)
    @pref.command()
    async def show(self, ctx:commands.Context, *, arg1=""): # asterisk is "consume rest" which allows multiple-word arguments without quotation marks
        author = ctx.author
        self.preferences = read_json("preferences", author)
        pref_num = await self.parse_arguments(ctx, arg1)

        # if invalid input
        if pref_num == -1:
            return
        
        # else if /pref show is used with "all", show list of all existing preferences
        if pref_num == 0:
            output_message = "These are your currently set preferences:"
            # reply in a more readable format than json
            for pref, value in self.preferences.items():
                if not isinstance(value, dict):
                    output_message += "\n\t"
                    output_message += ' '.join(pref.split('_')) # replace underscores with spaces
                    output_message += ": "
                    output_message += value
                # if single-nested json entry, unpack the nested dictionary too
                else:
                    output_message += "\n\t"
                    pref = ' '.join(pref.split('_')) # replace underscores with spaces
                    output_message += pref
                    for subpref, subvalue in value.items():
                        output_message += "\n\t\t"
                        output_message += ' '.join(subpref.split('_')) # replace underscores with spaces
                        output_message += ": "
                        output_message += subvalue
            await ctx.send(output_message)
            return

        # else if /pref show is used with a number or name, parse_arguments() should've converted it into a number and we try to match that
        pref, value = list(self.preferences.items())[pref_num - 1]
        if not isinstance(value, dict):
            output_message = f"This is your currently set preference for \""
            output_message += ' '.join(pref.split('_')) # replace underscores with spaces
            output_message += "\": "
            output_message += value
        # if single-nested json entry, unpack the nested dictionary too
        else:
            output_message = f"These are your currently set preferences for \""
            output_message += ' '.join(pref.split('_')) # replace underscores with spaces
            output_message += "\": "
            for subpref, subvalue in value.items():
                output_message += "\n\t"
                output_message += ' '.join(subpref.split('_')) # replace underscores with spaces
                output_message += ": "
                output_message += subvalue
        await ctx.send(output_message)
        return
    
    
    ####################################
    # /pref change: change preference(s)
    @pref.command()
    async def change(self, ctx:commands.Context, *, arg1=""):
        author = ctx.author
        self.preferences = read_json("preferences", author)
        pref_num = await self.parse_arguments(ctx, arg1)

        # if invalid input
        if pref_num == -1:
            return
        
        # else if /pref change is used with "all", run through list of all existing preferences
        if pref_num == 0:
            await self.set_timezone(ctx, author)
            await self.set_dow_or_date(ctx, author)
            await self.set_date_format(ctx, author)
            await self.set_time_format(ctx, author)
            await self.set_start_of_weeks(ctx, author)
            await self.set_default_due_time(ctx, author)
            await self.set_default_reminder_timing(ctx, author)
            await self.set_numbered_subjects(ctx, author)
            await self.set_numbered_tasks(ctx, author)
            await self.set_completion_ticks(ctx, author)
            await self.set_daily_todo_list_recap(ctx, author)
            await self.set_display_todo_list_when_updated(ctx, author)
            await ctx.send("You're all set up! Ping me for commands and help.")
            return

        # else if /pref change is used with a number or name, parse_arguments() should've converted it into a number and we try to match that
        await self.pref_change_switcher(ctx, author, pref_num)
        return
    
    
######################################################################################################################################################
#                                                                  ARGUMENT PARSER                                                                   #
######################################################################################################################################################


    #######################################################
    # parses user arguments for /pref show and /pref change
    async def parse_arguments(self, ctx:commands.Context, arg:str) -> int:

        # if the argument was "all" or blank, show/change all arguments
        if arg.lower() == "all" or arg == "":
            return 0

        # else if the argument is a number
        if arg.isdigit():
            arg = int(arg)
            if arg > 0 and arg <= len(self.preferences):
                return arg
            await ctx.send("what") # if number is invalid
            return -1
        
        # else if the argument is not a number and is a name, attempt to match it to a preference number
        item_counter = 0
        arg_length = len(arg)
        arg = arg.lower()
        arg = '_'.join(arg.split(' ')) # replace spaces with underscores since json uses underscores
        for k in self.preferences.keys():
            item_counter += 1
            if len(k) < (arg_length - 3): # if argument is longer than the preference name
                continue
            if arg == (k[3:3 + arg_length]).lower(): # else if match found
                return item_counter
        
        # else if match not found because of invalid argument
        await ctx.send("what")
        return -1


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
        self.preferences["1. Timezone"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"timezone\" set to: " + self.preferences["1. Timezone"])
        return
    
    
    ################################################
    # 2. function for setting DOW or date preference
    async def set_dow_or_date(self, ctx:commands.Context, author):
        await ctx.send("2. DOW or Date\n\t→ Enter \"DOW\" if you would like to have dates represented by days of the week, otherwise enter \"date\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "dow" or message_str == "date"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content)
        response = response.lower() if response.lower() == "date" else response.upper() # capitalize DOW
        self.preferences["2. DOW_or_date"] = response
        write_json("preferences", author, self.preferences) # write updated preferences into json every time in case "/pref change all" sequence is cut off for whatever reason
        # print confirmation
        await ctx.send("> Preference for \"DOW or date\" set to: " + self.preferences["2. DOW_or_date"])
        return
    

    ################################################
    # 3. function for setting date format preference
    async def set_date_format(self, ctx:commands.Context, author):
        await ctx.send("3. Date Format\n\t→ Enter \"YYYY-MM-DD\", \"MM-DD-YYYY\", or \"DD-MM-YYYY\", even if you've chosen DOW instead of dates")

        def check_response(message):
            message_str = (str(message.content)).upper()
            return message_str == "YYYY-MM-DD" or message_str == "MM-DD-YYYY" or message_str == "DD-MM-YYYY"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        response = str(response.content).upper()
        # save response to user preferences
        self.preferences["3. Date_format"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"date format\" set to: " + self.preferences["3. Date_format"])
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
        self.preferences["4. Time_format"] = str(response.content) + "-hour"
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"time format\" set to: " + self.preferences["4. Time_format"])
        return

    
    ##################################################
    # 5. function for setting start of week preference
    async def set_start_of_weeks(self, ctx:commands.Context, author):
        await ctx.send("5. Start of Week\n\t→ Enter \"sun\" or \"mon\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "sun" or message_str == "mon"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).capitalize()
        self.preferences["5. Start_of_week"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"start of week\" set to: " + self.preferences["5. Start_of_week"])
        return
    

    ##########################################
    # 6. function for setting default due time
    async def set_default_due_time(self, ctx:commands.Context, author):
        await ctx.send("6. Default Due Time\n\t→ Enter a time in either 12- or 24-hour format w/o seconds, e.g. \"1159 pm\" or \"23:59\"")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed timestr from the checking function
            response = await self.bot.wait_for("message")
            response = time_to_timestr(str(response.content).lower())
            valid = response != "error"
        # save response to user preferences json
        response = timestr_to_displaystr(response, self.preferences)
        self.preferences["6. Default_due_time"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"default due time\" set to: " + self.preferences["6. Default_due_time"])
        return
    

    #################################################
    # 7. function for setting default reminder timing
    async def set_default_reminder_timing(self, ctx:commands.Context, author):
        await ctx.send("7. Default Reminder Timing\n\t→ Enter a duration w/o seconds for the amount of time before a due date to send a reminder, e.g. \"2:00\" or \"0:45\". \"0\" means no reminders.")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed durstr from the checking function
            response = await self.bot.wait_for("message")
            response = dur_to_durstr(str(response.content))
            valid = response != "error"
        # save response to user preferences json
        response = durstr_to_displaystr(response)
        self.preferences["7. Default_reminder_timing"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"default reminder timing\" set to: " + self.preferences["7. Default_reminder_timing"])
        return
    

    ######################################################
    # 8. function for setting numbered subjects preference
    async def set_numbered_subjects(self, ctx:commands.Context, author):
        await ctx.send("8. Numbered Subjects\n\t→ Enter \"yes\" if you want subjects/task categories (besides \"other\" and \"others\") to be labeled numerically by alphabetical order (for easier access), else enter \"no\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).lower()
        self.preferences["8. Numbered_subjects"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"numbered subjects\" set to: " + self.preferences["8. Numbered_subjects"])
        return
    

    ###################################################
    # 9. function for setting numbered tasks preference
    async def set_numbered_tasks(self, ctx:commands.Context, author):
        await ctx.send("9. Numbered Tasks\n\t→ Enter \"yes\" if you want tasks to be labeled numerically by subject, due date, and then alphabetical order (for easier access), else enter \"no\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).lower()
        self.preferences["9. Numbered_tasks"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"numbered tasks\" set to: " + self.preferences["9. Numbered_tasks"])
        return
    

    #######################################################
    # 10a. function for setting completion ticks preference
    async def set_completion_ticks(self, ctx:commands.Context, author):
        await ctx.send("10a. Completion Ticks\n\t→ Enter \"yes\" if you want completed items to be ticked rather than immediately removed, otherwise enter \"no\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).lower()
        self.preferences["10. Completion_ticks"] = {"10a. Yes/No": response}
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"completion ticks\" set to: " + self.preferences["10. Completion_ticks"]["10a. Yes/No"])

        # follow-ups if "yes"
        if response == "yes":
            await self.set_tick_colors(ctx, author)
            await self.set_days_per_deletion_of_ticked_items(ctx, author)
        return
    

    ##################################################
    # 10b. function for setting tick colors preference
    async def set_tick_colors(self, ctx:commands.Context, author):
        await ctx.send("10b. Tick Colors\n\t→ Enter \"yes\" if you want ticks to be colored by day of week completed, otherwise enter \"no\"")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json as nested dictionary
        response = str(response.content).lower()
        self.preferences["10. Completion_ticks"]["10b. Colors"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"tick colors\" set to: " + self.preferences["10. Completion_ticks"]["10b. Colors"])
        return
    

    #################################################################################################################################
    # 10c. function for setting days per check for deleting ticked items (days since preferred start of week/last check for deletion)
    async def set_days_per_deletion_of_ticked_items(self, ctx:commands.Context, author):
        await ctx.send("10c. Days Per Deletion of Ticked Items\n\t→ Enter the number of days between each check to clear ticked items; e.g. 6 means clear once every 6 days starting the most recent " + self.preferences["5. Start_of_week"])

        def check_response(message):
            message_str = (str(message.content)).lower()
            if message_str.isdigit():
                if int(message_str) > 0:
                    return True
            return False
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json as nested dictionary
        response = str(response.content)
        self.preferences["10. Completion_ticks"]["10c. Days_per_deletion_of_ticked_items"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"days per deletion of ticked items\" set to: " + self.preferences["10. Completion_ticks"]["10c. Days_per_deletion_of_ticked_items"])
        return
    

    ############################################################
    # 11a. function for setting daily todo list recap preference
    async def set_daily_todo_list_recap(self, ctx:commands.Context, author):
        await ctx.send("11a. Daily Todo List Recap\n\t→ Enter \"yes\" if you want a daily todo list recap to be sent, otherwise enter \"no\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json as nested dictionary
        response = str(response.content).lower()
        self.preferences["11. Daily_todo_list_recap"] = {"11a. Yes/No": response}
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"daily todo list recap\" set to: " + self.preferences["11. Daily_todo_list_recap"]["11a. Yes/No"])

        # follow-up if "yes"
        if response == "yes":
            await self.set_daily_recap_time(ctx, author)
        return
    

    ######################################################
    # 11b. function for setting daily todo list recap time
    async def set_daily_recap_time(self, ctx:commands.Context, author):
        await ctx.send("11b. Daily Recap Time\n\t→ Enter a time in either 12- or 24-hour format w/o seconds, e.g. \"1100 am\" or \"15:15\"")

        # wait for a valid response from user
        valid = False
        while not valid: # not using built-in wait_for check since we want to return both the boolean and the processed timestr from the checking function
            response = await self.bot.wait_for("message")
            response = time_to_timestr(str(response.content).lower())
            valid = response != "error"
        # save response to user preferences json
        response = timestr_to_displaystr(response, self.preferences)
        self.preferences["11. Daily_todo_list_recap"]["11b. Daily_recap_time"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"daily recap time\" set to: " + self.preferences["11. Daily_todo_list_recap"]["11b. Daily_recap_time"])
        return
    

    ######################################################################
    # 12. function for setting diplaying todo list when updated preference
    async def set_display_todo_list_when_updated(self, ctx:commands.Context, author):
        await ctx.send("12. Display Todo List When Updated\n\t→ Enter \"yes\" if you would like me to display your updated todo list every time you make a change, otherwise enter \"no\".")

        def check_response(message):
            message_str = (str(message.content)).lower()
            return message_str == "yes" or message_str == "no"
        
        # wait for a valid response from user
        response = await self.bot.wait_for("message", check=check_response)
        # save response to user preferences json
        response = str(response.content).lower()
        self.preferences["12. Display_todo_list_when_updated"] = response
        write_json("preferences", author, self.preferences)
        # print confirmation
        await ctx.send("> Preference for \"display todo list when updated\" set to: " + self.preferences["12. Display_todo_list_when_updated"])
        return


######################################################################################################################################################
#                                                                  HELPER FUNCTIONS                                                                  #
######################################################################################################################################################


    #################################################################################################
    # match arguments in /pref change to preference-setting functions based on their numerical labels
    async def pref_change_switcher(self, ctx:commands.Context, author, arg_num):
        match arg_num:
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
                await self.set_numbered_subjects(ctx, author)
                return
            case 9:
                await self.set_numbered_tasks(ctx, author)
                return
            case 10:
                await self.set_completion_ticks(ctx, author)
                return
            case 11:
                await self.set_daily_todo_list_recap(ctx, author)
                return
            case 12:
                await self.set_display_todo_list_when_updated(ctx, author)
                return
        
        # if match not found because of invalid argument
        await ctx.send("what")
        return

from discord.ext import commands

from util.command_utils import *
from util.date_utils import *
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(Add(bot))


class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##################
    # /add: add a task
    @commands.command()
    async def add(self, ctx:commands.Context, *args):
        arg_length = len(args)

        # if an improper number of arguments is entered, return error
        if arg_length < 2:
            await ctx.send("> Too few arguments: the format is ```/add <subject> <task name> "\
                "<[optional] due date> <[optional] due time> <[optional] reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return
        if arg_length > 5:
            await ctx.send("> Too many arguments: the format is ```/add <subject> <task name> "\
                "<[optional] due date> <[optional] due time> <[optional] reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return


######################################################################################################################################################
#                                                                  ARGUMENT PARSER                                                                   #
######################################################################################################################################################


    ################################################################################
    # parses user arguments for /add and unscrambles optional arguments if necessary
    async def parse_arguments(self, ctx:commands.Context, args:list) -> tuple[str, str, str, str]:
        arg_length = len(args)

        # if an improper number of arguments is entered, return error
        if arg_length < 2:
            await ctx.send("> Too few arguments: the format is ```/add <subject> <task name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return ("", "", "", "error")
        if arg_length > 5:
            await ctx.send("> Too many arguments: the format is ```/add <subject> <task name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return ("", "", "", "error")

        subject_name = ''.join(args[0].lower().split(' ')) # strip spaces
        subject_defaults = []
        name = args[1]
        due_date = ""
        due_time = ""
        reminder_timing = ""

        # determine existence of subject and prepare to create a new one if it doesn't exist
        author = ctx.author
        todo_list = read_json("todolists", author)
        numbered_subjects = read_json("preferences", author)["8. Numbered_subjects"] == "yes"
        subject_len = len(subject_name)
        subject_exists = False
        for existing_subject_name, existing_subject_value in todo_list.items():
            if numbered_subjects: # strip numerical label
                existing_key = ''.join(existing_key.split(' ')[1:])
            if ''.join(existing_subject_name.lower().split(' '))[:subject_len] == subject_name: # strip spaces and match length
                subject_name = existing_subject_name # make sure authentic name of subject is sent back (no stripped spaces/numerical label)
                subject_exists = True
                for subvalue in list(existing_subject_value.values())[:3]: # pull subject defaults, which are the first 3 subvalues of subject
                    subject_defaults.append(subvalue)
                break

        # unscramble optional argument order
        if arg_length > 2:
            for arg in args[2:]:
                # assign due time or reminder timing whenever a colon is detected, prioritizing due time since it comes first
                if ':' in arg:
                    if time_to_timestr(arg) != "error" and due_time == "":
                        due_time = time_to_timestr(arg)
                    elif dur_to_durstr(arg) != "error" and reminder_timing == "":
                        reminder_timing = dur_to_durstr(arg)
                    else:
                        await ctx.send(f"> Invalid argument: ```{arg}```")
                        return ("", "", "", "error")
                # assign due date or due time otherwise (reminder timing has to have a colon since it's a duration), prioritizing due date since it comes first
                else:
                    if date_to_datestr(arg) != "error" and due_date == "":
                        due_date = date_to_datestr(author, arg)
                    elif time_to_timestr(arg) != "error" and due_time == "":
                        due_time = time_to_timestr(arg)
                    else:
                        await ctx.send(f"> Invalid argument: ```{arg}```")
                        return ("", "", "", "error")
                    
        # create new subject if it didn't exist; do this at the end so that this task's defaults also initialize that subject's defaults
        if not subject_exists:
            # if user didn't specify a due date for the task (since there's no default for subjects), return error
            if due_date == "":
                await ctx.send(f"> Missing task's due date: new subject \"{subject_name}\" has no default due date. The format is ```/add <subject> <task name> "\
                    "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                    "Remember to use quotation marks around multi-word arguments, and the escape character "\
                    "\ before any other quotation marks that are to be included in arguments.")
                return ("", "", "", "error")
            # and if the task had no defaults, pull both subject and task defaults from preferences
            if due_time == "" or reminder_timing == "":
                preferences = read_json("preferences", ctx.author)
                if due_time == "":
                    due_time = time_to_timestr(preferences["6. Default_due_time"])
                if reminder_timing == "":
                    reminder_timing = dur_to_durstr(preferences["7. Default_reminder_timing"])
            # add new subject into list with this task's defaults
            todo_list = create_todo_list_subject(author, todo_list, [subject_name, due_date, due_time, reminder_timing])
            if todo_list == {"error": "error"}:
                await ctx.send("Congratulations, you found a bug. Here's some cake 🎂\n\nDM AnonymousRand#1803 if you feel like it")
                return
        
        # else if subject exists but user didn't provide a due date/due time/reminder timing, pull it from subject default
        elif due_time == "" or due_time == "" or reminder_timing == "":
            # if user didn't specify a due date for the task and its subject also does not have a default due date, return error
            if due_date == "":
                if subject_defaults[0] == "":
                    await ctx.send(f"> Missing task's due date: subject \"{subject_name}\" has no default due date. The format is ```/add <subject> <task name> "\
                        "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                        "Remember to use quotation marks around multi-word arguments, and the escape character "\
                        "\ before any other quotation marks that are to be included in arguments.")
                    return ("", "", "", "error")
                due_date = subject_defaults[0]
            if due_time == "":
                due_time = subject_defaults[1]
            if reminder_timing == "":
                reminder_timing = subject_defaults[2]

        return (name, due_date, due_time, reminder_timing)
        
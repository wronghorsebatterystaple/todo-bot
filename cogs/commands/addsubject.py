from discord.ext import commands

from util.command_utils import *
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(Addsubject(bot))


class Addsubject(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.todo_list = {} # dictionary to read and write command caller's todo list to json


######################################################################################################################################################
#                                                                      COMMAND                                                                       #
######################################################################################################################################################


    ############################
    # /addsubject: add a subject
    @commands.command()
    async def addsubject(self, ctx:commands.Context, *args):
        arg_length = len(args)
        
        # parse arguments and make they are of the correct format/order and pulling in absent default due time/reminder timing arguments from preferences
        args_processed = await self.parse_arguments(ctx, args)
        if args_processed[3] == "error":
            return

        # enter into dictionary, resorting categories and addding numerical label if necessary
        author = ctx.author
        self.todo_list = enter_todo_list_subject(author, read_json("todolists", author), args_processed)
        if self.todo_list == {"error": "error"}:
            await ctx.send("Congratulations, you found a bug. Here's a cookie 🍪\n\nDM AnonymousRand#1803 if you feel like it\n\nʸᵉˢ ᵐʸ ᵉʳʳᵒʳ ᶜᵒᵈᵉ ⁱˢ ᶜᵒᵒᵏⁱᵉ")
            return
        
        # write to todo list json
        write_json("todolists", author, self.todo_list)

        # print confirmation
        await ctx.send("> Subject \"" + args_processed[0] + "\" added to todo list")
        return


######################################################################################################################################################
#                                                                  ARGUMENT PARSER                                                                   #
######################################################################################################################################################


    #######################################################################################
    # parses user arguments for /addsubject and unscrambles optional arguments if necessary
    async def parse_arguments(self, ctx:commands.Context, args:list) -> tuple[str, str, str, str]:
        arg_length = len(args)

        # if an improper number of arguments is entered, return error
        if arg_length < 1:
            await ctx.send("> Too few arguments: the format is ```/addsubject <subject name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return ("", "", "", "error")
        if arg_length > 4:
            await ctx.send("> Too many arguments: the format is ```/addsubject <subject name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return ("", "", "", "error")

        name = args[0]
        default_due_date = ""
        default_due_time = ""
        default_reminder_timing = ""

        # unscramble optional argument order
        if arg_length > 1:
            print("unscrambling...")
            for arg in args[1:]:
                print("current arg:", arg)

                # assign due time or reminder timing whenever a colon is detected, prioritizing due time since it comes first
                if ':' in arg:
                    print("colon")
                    if time_to_timestr(arg) != "error" and default_due_time == "":
                        print("assigned to time")
                        default_due_time = time_to_timestr(arg)
                    elif dur_to_durstr(arg) != "error" and default_reminder_timing == "":
                        print("assigned to reminder timing")
                        default_reminder_timing = dur_to_durstr(arg)
                    else:
                        await ctx.send(f"> Invalid argument: ```{arg}```")
                        return ("", "", "", "error")

                # assign due date or due time otherwise (reminder timing has to have a colon since it's a duration), prioritizing due date since it comes first
                else:
                    print("not colon")
                    if date_to_datestr(arg) != "error" and default_due_date == "":
                        print("assigned to date")
                        default_due_date = date_to_datestr(arg)
                    elif time_to_timestr(arg) != "error" and default_due_time == "":
                        print("assigned to time")
                        default_due_time = time_to_timestr(arg)
                    else:
                        await ctx.send(f"> Invalid argument: ```{arg}```")
                        return ("", "", "", "error")

        # if user didn't provide a default due time/reminder timing, pull it from preferences
        # there is no default due date preference since it tends to be much more variable
        if default_due_time == "" or default_reminder_timing == "":
            preferences = read_json("preferences", ctx.author)
            if default_due_time == "":
                default_due_time = time_to_timestr(preferences["6. Default_due_time"])
            if default_reminder_timing == "":
                default_reminder_timing = dur_to_durstr(preferences["7. Default_reminder_timing"])

        return (name, default_due_date, default_due_time, default_reminder_timing)
        
from discord.ext import commands
from util.command_utils import *
from util.json_utils import *
from util.time_utils import *


async def setup(bot):
    await bot.add_cog(Command(bot))


class Command(commands.Cog):
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
        print("1", args)

        # if an improper number of arguments is entered, return error
        if arg_length < 1:
            await ctx.send("> Too few arguments: the format is ```/addsubject <subject name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return
        if arg_length > 4:
            await ctx.send("> Too many arguments: the format is ```/addsubject <subject name> "\
                "<[optional] default due date> <[optional] default due time> <[optional] default reminder timing>```"\
                "Remember to use quotation marks around multi-word arguments, and the escape character "\
                "\ before any other quotation marks that are to be included in arguments.")
            return
        
        print("2")
        # parse arguments and make they are of the correct format/order
        args_processed = await self.parse_arguments(ctx, args)
        if args_processed[3] == "error":
            return
        
        print("3")
        # enter into dictionary
        author = ctx.author
        self.todo_list = read_json("todolists", author)
        self.todo_list[args_processed[0]] =\
                    {"Default_due_date": args_processed[1],
                    "Default_due_time": args_processed[2],
                    "Default_reminder_timing": args_processed[3]}

        print("4")
        # resort categories and add numerical label if necessary
        self.todo_list = sort_todo_list_subjects(author, self.todo_list)
        self.todo_list = add_numerical_labels_subjects(author, self.todo)
        
        print("5")
        # write to todo list json
        write_json("todolists", author, self.todo_list)
        print("6")

        # print confirmation
        await ctx.send(f"> work on this later")
        return


######################################################################################################################################################
#                                                                  ARGUMENT PARSER                                                                   #
######################################################################################################################################################


    #######################################################################################
    # parses user arguments for /addsubject and unscrambles optional arguments if necessary
    async def parse_arguments(self, ctx:commands.Context, args:list) -> tuple[str, str, str, str]:
        print("received")
        arg_length = len(args)

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

        return (name, default_due_date, default_due_time, default_reminder_timing)


######################################################################################################################################################
#                                                        BEFORE/AFTER COMMAND INVOKE FUNCTIONS                                                       #
######################################################################################################################################################
# must do this for every file instead of having a master command group because command groups don't seem to carry between files


    ########################################################################################################################################
    # prevent other commands from being called during command runtimes by setting command prefix to <Null> for the duration of every command
    @addsubject.before_invoke
    async def disable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '\u0000'


    ########################
    # restore command prefix
    @addsubject.after_invoke
    async def enable_commands(self, ctx:commands.Context):
        self.bot.command_prefix = '/'
    

    ######################################################################################
    # make sure users have fully set their preferences before trying to do todo list stuff
    @addsubject.before_invoke
    async def check_prefs(self, ctx:commands.Context):
        await check_prefs_exist(ctx)
        
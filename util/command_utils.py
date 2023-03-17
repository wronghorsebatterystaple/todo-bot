import os

from discord.ext import commands

from util.date_utils import *
from util.json_utils import *
from util.time_utils import *


######################################################################################################################################################
#                                                             SUBJECT COMMAND FUNCTIONS                                                              #
######################################################################################################################################################


##########################
# sorts todo list subjects
def sort_todo_list_subjects(author:str, todo_list:dict) -> dict:
    {kv_pair[0]: kv_pair[1] for kv_pair in sorted(todo_list.items(), key=lambda item: item[0])}
    todo_list_processed = {}
    print("4.1")
    pass


##################################
# add numerical labels to subjects
def add_numerical_labels_subjects(author:str, todo_list:dict) -> dict:
    pass


######################################################################################################################################################
#                                                               TASK COMMAND FUNCTIONS                                                               #
######################################################################################################################################################


#########################################
# sorts todo list subjects and then tasks
def sort_todo_list_tasks(author:str, todo_list:dict) -> dict:
    sort_todo_list_subjects(author, dict)
    pass


###############################
# add numerical labels to tasks
def add_numerical_labels_tasks(author:str, todo_list:dict) -> dict:
    pass

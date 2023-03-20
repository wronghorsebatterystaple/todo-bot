from util.json_utils import *


######################################################################################################################################################
#                                                                 SUBJECT FUNCTIONS                                                                  #
######################################################################################################################################################


#############################################################################
# enters todo list subject into dictionary in the right spot to remain sorted
def create_todo_list_subject(author:str, todo_list:dict, new_entry:tuple[str, str, str, str]) -> dict:
    new_todo_list = {} # new dictionary to store updated todo list
    new_entry_name = new_entry[0]
    numbered_subjects = read_json("preferences", author)["8. Numbered_subjects"] == "yes"
    inserted = False
    counter = 0 # for adding numerical labels

    # if the todo list is empty or the new subject is named "other" or "others", add it in at the end
    if len(todo_list.items()) == 0 or new_entry_name.lower() == "other" or new_entry_name.lower() == "others":
        new_todo_list = todo_list
        counter = len(todo_list.items())
        if numbered_subjects:
            new_entry_name = str(counter + 1) + ". " + new_entry_name

        new_todo_list[new_entry_name] = {\
            "Default_due_date": new_entry[1],
            "Default_due_time": new_entry[2],
            "Default_reminder_timing": new_entry[3]}
        
        return new_todo_list
    
    # else iterate through list to find the right insertion spot
    for existing_subject_name, existing_subject_value in todo_list.items():
        counter += 1
        
        # no need to continue comparing alphabetical orders if insertion spot has already been found
        # and only copy in the rest of the dict with updated numerical labels
        if inserted:
            if numbered_subjects:
                new_todo_list[str(counter) + ". " + ''.join(existing_subject_name.split(' ')[1:])] = existing_subject_value
            continue
        
        # else if insertion spot has not been found, compare entry to be inserted alphabetically with each existing entry as we iterate
        else:
            if numbered_subjects: # strip numerical label for alphabetical comparison
                existing_subject_name = ''.join(existing_subject_name.split(' ')[1:])

            # if the new entry is alphabetically before the current entry being iterated over, insert new entry before current entry
            # also make sure to keep "other" abnd "others" subjects at the very bottom (this also prevents a bug)
            if new_entry_name < existing_subject_name or existing_subject_name.lower() == "other" or existing_subject_name.lower() == "others":
                if numbered_subjects:
                    new_entry_name = str(counter) + ". " + new_entry_name
                new_todo_list[new_entry_name] = {\
                    "Default_due_date": new_entry[1],
                    "Default_due_time": new_entry[2],
                    "Default_reminder_timing": new_entry[3]}
                inserted = True
                counter += 1 # update numerical label for current key, value entry which is gonna be inserted in next
            
            # copy in current key, value entry
            if numbered_subjects: # put back numerical label if necessary
                existing_subject_name = str(counter) + ". " + existing_subject_name
            new_todo_list[existing_subject_name] = existing_subject_value
    
    # bug catching if insertion point not found
    if not inserted:
        return {"error": "error"}

    return new_todo_list


######################################################################################################################################################
#                                                                   TASK FUNCTIONS                                                                   #
######################################################################################################################################################


##########################################################################
# enters todo list task into dictionary in the right spot to remain sorted
def create_todo_list_task(author:str, todo_list:dict) -> dict:
    create_todo_list_subject(author, dict)
    pass


###############################
# add numerical labels to tasks
def add_numerical_labels_tasks(author:str, todo_list:dict) -> dict:
    pass

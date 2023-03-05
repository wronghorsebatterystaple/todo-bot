######################################################################################################################################################
#                                                                   TIME FUNCTIONS                                                                   #
######################################################################################################################################################


################################################################################################################
# determine if an inputted time is valid and convert it to a 4-digit 24-hour time string (e.g. "2359" or "0800")
def time_to_timestr(time:str) -> str:
    timestr = ""
    twelve = False
    colon = False
    minute_digits = 0
    total_digits = 0

    for i in range(len(time)):
        char = time[i]
        if char.isnumeric():
            timestr += char
            total_digits += 1
            if colon:
                minute_digits += 1
        elif char == ':':
            colon = True
        elif char == 'a' or char == 'p':
            timestr += char
            twelve = True
            # if 'a'/'p' or "am"/"pm" aren't the last char(s) of the input, return invalid response (e.g. 2a:59, 9p0)
            if i < len(time) - 1:
                if i == len(time) - 2 and time[i + 1] != 'm':
                    return "error"
            
            # else safe to assume that this is the last meaningful character of the response that we need to parse
            break

        # if any character besides a number, ' ', ':', 'a', or 'p' is detected, return invalid response (e.g. 2f2, abc, -124s, !^%~)
        elif char != ' ':
            return "error"
    
    # if no numeric characters entered, return invalid response (e.g. ::,    , a, p)
    if timestr == "" or timestr == "a" or timestr == "p":
        return "error"
    
    # if there are no minutes, assume user inputted the hour and automatically add zeroes for minutes (e.g. 12p -> 1200p, 13 -> 1300, 5 -> 500:)
    if (not colon and (total_digits < 3)) or (colon and minute_digits == 0):
        timestr = timestr[0:total_digits] + "00" + timestr[total_digits:]
        minute_digits = 2
        total_digits += 2
    
    # if there is no colon, assume the last 2 digits are minutes (e.g. 1200, 1159am, 245, 130p)
    if not colon and total_digits >= 3:
        minute_digits = 2
    
    # if there aren't 0-2 hour digits and 0/2 minute digits, return invalid response (e.g. 245:15, 23:5, 8:344, 15:30:00)
    if minute_digits > 2 or total_digits - minute_digits > 2 or minute_digits == 1:
        return "error"
    
    # else add leading zeros if not 4 digits, as we can now safely asssume that all the user-inputted digits fill up the minute side first (e.g. 130p -> 0130p, 245 -> 0245)
    while total_digits < 4:
        timestr = "0" + timestr
        total_digits += 1

    # split hours and minutes for later analysis
    hours = int(timestr[:2])
    minutes = timestr[2:]
    
    # convert to 24-hour if it was in 12-hour ('a'/'p' detected) for ease of validation and storing
    if twelve:
        # if user entered a 12-hour time with greater than 12 hours, return invalid response (e.g. 23pm, 13:05am, 15p)
        if hours > 12:
            return "error"
        minutes += "m" # append an "m" for ease of twelve_to_24()
        hours, minutes = twelve_to_24(hours, minutes)
        timestr = hours + minutes
    
    # if hours and minutes aren't within a valid range, return invalid response (e.g. 24:00, 4599, 12:60a)
    hours = int(hours)
    minutes = int(minutes)
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        return "error"
    
    # what is left should be free of edge cases
    # (should)
    return timestr


##################################################################################################
# convert a 4-digit 24-hour time string to display string with ":" and also "am"/"pm" if necessary
def timestr_to_displaystr(timestr:str, prefs:dict) -> str:
    hours = int(timestr[:2])
    minutes = timestr[2:]

    # convert to 12-hour if that is the user preference
    if "3. Time_format" in prefs.keys():
        if prefs["3. Time_format"] == "12-hour":
            hours, minutes = twentyfour_to_12(hours, minutes)
    
    hours = str(hours)
    # since single-digit integers are automatically shortened but we want to preserve the 2 digits
    if len(hours) < 2:
        hours = "0" + hours
    
    # add colons
    timestr = str(hours) + ":" + minutes
    return timestr


######################################################################################################################################################
#                                                                 DURATION FUNCTIONS                                                                 #
######################################################################################################################################################


############################################################################################################
# determine if an inputted duration is valid and convert it to a 4-digit duration string (e.g. 0200 or 0030)
def dur_to_durstr(dur:str) -> str:
    durstr = ""
    colon = False
    minute_digits = 0
    hour_digits = 0

    for char in dur:
        if char.isnumeric():
            durstr += char
            if colon:
                minute_digits += 1
            else:
                hour_digits += 1
        elif char == ':':
            colon = True
        # if any character besides a number, ' ', or ':' is detected, return invalid response (e.g. 2f2, abc, -124s, !^%~)
        elif char != ' ':
            return "error"
    
    # if there is no colon, return invalid response (e.g. 300, 1, 30)
    if not colon:
        return "error"
    
    # if there aren't 0-2 hour digits and 2 minute digits, return invalid response (e.g. 233:10, 1:0, 2:30:30)
    if minute_digits < 2 or minute_digits > 2 or hour_digits > 2 or hour_digits < 0:
        return "error"
    
    # else add leading zeros if there are less than 2 hour digits (e.g. 2:00 -> 02:00, :30 -> 00:30)
    while hour_digits < 2:
        durstr = "0" + durstr
        hour_digits += 1
    
    # what is left should be free of edge cases
    return durstr


##############################################################
# convert a 4-digit duration string to display string with ":"
def durstr_to_displaystr(durstr:str) -> str:
    # add colons
    hours = durstr[:2]
    minutes = durstr[2:]
    return hours + ":" + minutes


######################################################################################################################################################
#                                                                  HELPER FUNCTIONS                                                                  #
######################################################################################################################################################


############################################################
def twelve_to_24(hours:int, minutes:str) -> tuple[str, str]:
    if minutes[-2] == 'p':
        hours = str(hours + 12)
    else:
        hours = str(hours)

    # shave off the am/pm
    minutes = minutes[:-2]

    # since 12am (hours = 12) in 12-hour is 00:00 in 24-hour
    if hours == "12":
        hours = "00"

    # since 12pm (hours = 24) in 12-hour is 12:00 in 24-hour
    if hours == "24":
        hours = "12"

    # since single-digit integers are automatically shortened but we want to preserve the 2 digits
    if len(hours) < 2:
        hours = "0" + hours

    return hours, minutes


################################################################
def twentyfour_to_12(hours:int, minutes:str) -> tuple[str, str]:
    if hours > 12:
        hours = str(hours - 12)
        minutes = minutes + "pm"
    else:
        hours = str(hours)
        minutes = minutes + "am"
    
    # since 12:00 in 24-hour is 12:00pm in 12-hour
    if hours == "12":
        minutes = minutes[:-2] + "pm"

    # since 00:00 in 24-hour is 12:00am in 12-hour
    if hours == "0":
        hours = "12"

    # since single-digit integers are automatically shortened but we want to preserve the 2 digits
    if len(hours) < 2:
        hours = "0" + hours

    return hours, minutes


###########################################
def durstr_to_minutestr(durstr:str) -> str:
    hours = int(durstr[:2])
    minutes = int(durstr[2:])
    return str(hours * 60 + minutes)

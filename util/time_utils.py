######################################################################################################################################################
#                                                                   TIME FUNCTIONS                                                                   #
######################################################################################################################################################


################################################################################################################
# determine if an inputted time is valid and convert it to a 4-digit 24-hour time string (e.g. "2359" or "0800")
async def time_to_timestr(time:str) -> str:
    timestr = ""
    twelve = False
    colon = False
    minute_digits = 0
    hour_digits = 0
    total_digits = 0

    for i in range(len(time)):
        char = time[i]
        if char.isdigit():
            timestr += char
            total_digits += 1
            if colon:
                minute_digits += 1
            else:
                hour_digits += 1
        elif char == ':':
            colon = True
        elif char == 'a' or char == 'p':
            timestr += char
            twelve = True
            # if 'a'/'p' are found somewhere besides the last char(s) of the input, return invalid response (e.g. 2a:59, 9p0)
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
    
    # if there are no minutes, assume user inputted the hour and automatically add zeroes for minutes (e.g. 12p -> 1200p, 13 -> 1300, 5 -> 500)
    if not colon and (total_digits < 3):
        # "11" -> "11" + "00" + ""
        # "11p" -> "11" + "00" + "p"
        timestr = timestr[0:total_digits] + "00" + timestr[total_digits:]
        minute_digits = 2
        total_digits += 2
    elif colon and minute_digits == 0:
        # "1:"" -> "1:"" + "00" + ""
        # "12:p" -> "12:" + "00" + "p"
        timestr = timestr[0:total_digits + 1] + "00" + timestr[total_digits + 1:]
        minute_digits = 2
        total_digits += 2
    
    # if there is no colon, assume the last 2 digits are minutes and the remaning are hours (e.g. 1200, 11510am, 245, 130p)
    if not colon and total_digits >= 3:
        minute_digits = 2
        hour_digits = hour_digits - minute_digits
    
    # if there aren't 0-2 hour digits and 0/2 minute digits (or only 2 after the previous processing), return invalid response (e.g. 245:15, 23:5, 8:344, 15:30:00)
    if hour_digits > 2 or minute_digits != 2:
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
        hours, minutes = twelve_to_24str(hours, minutes)
        timestr = hours + minutes
    
    # if hours and minutes aren't within a valid range, return invalid response (e.g. 24:00, 4599, 12:60a)
    hours = int(hours)
    minutes = int(minutes)
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        return "error"
    
    # what is left should be free of edge cases
    # (should)
    return timestr


######################################################################################################################################################################
# convert a 4-digit 24-hour time string to display string with ":" and also "am"/"pm" if necessary (e.g. "2359" -> "23:59" in 24-hour, "0800" -> "08:00am" in 12-hour)
def timestr_to_displaystr(timestr:str, prefs:dict) -> str:
    hours = int(timestr[:2])
    minutes = timestr[2:]

    # convert to 12-hour if that is the user preference
    if "4. Time_format" in prefs.keys():
        if prefs["4. Time_format"] == "12-hour":
            hours, minutes = twentyfour_to_12str(hours, minutes)
    
    hours = str(hours)
    # since single-digit integers are automatically shortened but we want to preserve the 2 digits
    if len(hours) < 2:
        hours = "0" + hours
    
    # add colon
    timestr = str(hours) + ":" + minutes
    return timestr


######################################################################################################################################################
#                                                                 TIMEZONE FUNCTIONS                                                                 #
######################################################################################################################################################


####################################################################################################################################
# determine if an inputted timezone offset is valid and convert it to a 5-character timezone offset string (e.g. "-0800" or "+1400")
def tz_to_tzstr(tz:str) -> str:
    tzstr = ""
    negative = False
    colon = False
    minute_digits = 0
    hour_digits = 0
    total_digits = 0

    for i in range(len(tz)):
        char = tz[i]
        if char.isdigit():
            tzstr += char
            total_digits += 1
            if colon:
                minute_digits += 1
            else:
                hour_digits += 1
        elif char == ':':
            colon = True

        # if '+'/'-' are found somewhere besides the first char of the input, return invalid response (e.g. ++4:00, -3-30)
        elif char == '+':
            if i != 0:
                return "error"         
        elif char == '-':
            if i != 0:
                return "error"
            else:
                negative = True

        # if any character besides a number, '+', '-', ' ', or ':' is detected, return invalid response (e.g. 2f2, abc, -124s, !^%~)
        elif char != ' ':
            return "error"
    
    # if no numeric characters entered, return invalid response (e.g. ::,    , a, p)
    if tzstr == "":
        return "error"
    
    # if there are no minutes, assume user inputted the hour and automatically add zeroes for minutes (e.g. 12 -> 1200, 13 -> 1300, 5 -> 500)
    if not colon and (total_digits < 3):
        # "11" -> "11" + "00"
        tzstr = tzstr[0:total_digits] + "00"
        minute_digits = 2
        total_digits += 2
    elif colon and minute_digits == 0:
        # "1:"" -> "1:"" + "00"
        tzstr = tzstr[0:total_digits + 1] + "00"
        minute_digits = 2
        total_digits += 2
    
    # if there is no colon, assume the last 2 digits are minutes and the remaning are hours (e.g. 1200, 130)
    if not colon and total_digits >= 3:
        minute_digits = 2
        hour_digits = hour_digits - minute_digits
    
    # if there aren't 0-2 hour digits and 0/2 minute digits (or only 2 after the previous processing), return invalid response (e.g. 245:15, 23:5, 8:344, 15:30:00)
    if hour_digits > 2 or minute_digits != 2:
        return "error"
    
    # else add leading zeros (after signs) if not 4 digits, as we can now safely asssume that all the user-inputted digits fill up the minute side first (e.g. 130 -> 0130, -245 -> -0245)
    while total_digits < 4:
        tzstr = "0" + tzstr
        total_digits += 1

    # split hours and minutes for later analysis
    hours = tzstr[:2]
    minutes = tzstr[2:]
    
    # if hours and minutes aren't within a valid range, return invalid response (e.g. 15:00, -4599, 12:60)
    hours = int(hours)
    minutes = int(minutes)
    if hours < 0 or hours > 14 or minutes < 0 or minutes > 59:
        return "error"
    
    # what is left should be free of edge cases
    # (should)

    if negative:
        return "-" + tzstr
    else:
        return "+" + tzstr


###########################################################################################################################################################
# convert a 5-character timezone offset string to display string with "UTC" appended in front and ":" (e.g. "-0800" -> "UTC-08:00", "+1400" -> "UTC+14:00")
def tzstr_to_displaystr(tzstr:str) -> str:
    hours = tzstr[:3]
    minutes = tzstr[3:]
    
    # add "UTC" and colon
    tzstr = "UTC" + hours + ":" + minutes
    return tzstr


######################################################################################################################################################
#                                                                 DURATION FUNCTIONS                                                                 #
######################################################################################################################################################


################################################################################################################
# determine if an inputted duration is valid and convert it to a 4-digit duration string (e.g. "0200" or "0030")
def dur_to_durstr(dur:str) -> str:
    durstr = ""
    colon = False
    minute_digits = 0
    hour_digits = 0
    total_digits = 0

    for char in dur:
        if char.isdigit():
            durstr += char
            total_digits += 1
            if colon:
                minute_digits += 1
            else:
                hour_digits += 1
        elif char == ':':
            colon = True
            
        # if any character besides a number, ' ', or ':' is detected, return invalid response (e.g. 2f2, abc, -124s, !^%~)
        elif char != ' ':
            return "error"
    
    # if the user entered any number of zeros, this is a special case for no reminders
    if durstr.isdigit():
        if int(durstr) == 0:
            return "0000"

    # else if there is no colon, return invalid response (e.g. 300, 1, 30)
    if not colon:
        return "error"
    
    # else if there is a colon but no minutes, assume user inputted the hour and automatically add zeroes for minutes (e.g. 12: -> 1200, 5: -> 500)
    if (not colon and (total_digits < 3)) or (colon and minute_digits == 0):
        durstr = durstr[0:total_digits] + "00" + durstr[total_digits:]
        minute_digits = 2
        total_digits += 2
    
    # if there aren't 0-2 hour digits and 0/2 minute digits (or only 2 after the previous processing), return invalid response (e.g. 233:10, 1:0, 2:30:30)
    if hour_digits > 2 or minute_digits != 2:
        return "error"
    
    # else add leading zeros if there are less than 2 hour digits (e.g. 2:00 -> 02:00, :30 -> 00:30)
    while hour_digits < 2:
        durstr = "0" + durstr
        hour_digits += 1
    
    # what is left should be free of edge cases
    return durstr


##########################################################################################################
# convert a 4-digit duration string to display string with ":" (e.g. "0200" -> "02:00", "0030" -> "00:30")
def durstr_to_displaystr(durstr:str) -> str:
    hours = durstr[:2]
    minutes = durstr[2:]

    # add colon
    return hours + ":" + minutes


######################################################################################################################################################
#                                                                  HELPER FUNCTIONS                                                                  #
######################################################################################################################################################


###############################################################
def twelve_to_24str(hours:int, minutes:str) -> tuple[str, str]:
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


###################################################################
def twentyfour_to_12str(hours:int, minutes:str) -> tuple[str, str]:
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


########################################################################################################
# converts UTC offset to 24-hour UTC time at that offset's midnight (e.g. UTC-08:00 -> 8:00, UTC+04:15 -> 19:45)
def tzdisplaystr_to_24int(tzstr:str) -> tuple[int, int]:
    hours = -int(tzstr[3:6])
    minutes = int(tzstr[7:])
    if tzstr[3] == '+':
        hours += 23
        if minutes != 0:
            minutes = 60 - minutes
    return hours, minutes


##################################################
def durdisplaystr_to_minuteint(durstr:str) -> int:
    hours = int(durstr[:2])
    minutes = int(durstr[3:])
    return hours * 60 + minutes

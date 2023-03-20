# this would all probably be so much easier if I knew regex
# never mind https://stackoverflow.com/questions/15491894/regex-to-validate-date-formats-dd-mm-yyyy-dd-mm-yyyy-dd-mm-yyyy-dd-mmm-yyyy
from datetime import datetime
import re

from util.json_utils import *


def date_to_datestr(author:str, date:str) -> str:
    datestr = ""
    date = date.lower()

    # check if DOW format
    if date.startswith("mon"): return "Monday"
    if date.startswith("tue"): return "Tuesday"
    if date.startswith("wed"): return "Wednesday"
    if date.startswith("thu"): return "Thursday"
    if date.startswith("fri"): return "Friday"
    if date.startswith("sat"): return "Saturday"
    if date.startswith("sun"): return "Sunday"
    # else parse date according to user's date format preferences

    # convert preferred date format to one understood by datetime.datetime.strptime
    date_format = read_json("preferences", author)["3. Date_format"]
    strptime_date_format_Y = "" # this one assumes 4 digit year, while lowercase 'y' assumes 2 digit year
    strptime_date_format_y = ""
    for section in date_format.split('-'):
        if 'Y' in section:
            strptime_date_format_Y += "%Y-"
            strptime_date_format_y += "%y-"
            continue
        if 'M' in section:
            strptime_date_format_Y += "%m-"
            strptime_date_format_y += "%m-"
            continue
        if 'D' in section:
            strptime_date_format_Y += "%d"
            strptime_date_format_y += "%d"
            continue
    
    # convert user's input into one using the '-' delimiter between date sections in order to match our strptime format

    return datestr

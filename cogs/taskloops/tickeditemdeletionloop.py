import os
import time
import datetime

from discord.ext import commands, tasks
from util.json_utils import *
from util.time_utils import *


times = [datetime.time(hour=0, minute=0, second=0)] # must be global for @tasks.loop(), and must be initialized with something so cog doesn't raise error
# because @tasks.loop() is parsed before call to self.update_all()


async def setup(bot):
    await bot.add_cog(TickedItemDeletionLoop())


class TickedItemDeletionLoop(commands.Cog):
    def __init__(self):
        global times
        self.users_offsets = {} # dictionary to match the UTC times when users hit midnight (as (hours, minutes) tuples) to users
        times = [] # reset the times list; seems hacky but don't want to have to make update_all() and therefore users_offsets static as well
        self.update_all()

        # start taskloops
        if not self.check_ticked_item_deletion.is_running():
            self.check_ticked_item_deletion.start()
        if not self.check_updated_prefs.is_running():
            self.check_updated_prefs.start()

    
######################################################################################################################################################
#                                                                TASK LOOP FUNCTIONS                                                                 #
######################################################################################################################################################


    #########################################################################################################################################
    # every midnight for every user, check if that user wanted ticked items and whether their "days per deletion of ticked items" timer is up
    @tasks.loop(time=times)
    async def check_ticked_item_deletion(self):
        now_local = datetime.datetime.now()
        now_utc = datetime.datetime.utcnow()
        current_users_at_midnight = []

        # get a list of all the users who are currently at midnight, using self.users_offsets
        for username, *offset in self.users_offsets.items(): # asterisks unpacks tuple arguments
            for hour, minute in offset:
                if hour == now_utc.hour and minute == now_utc.minute:
                    current_users_at_midnight.append(username)

        # for each of these users, check if they wanted ticked items and whether their "days per deletion of ticked items" timer is up
        for username in current_users_at_midnight:
            
            # if user did not want ticked items and rather wanted items to just be deleted immediately (or didn't finish setup), no need to do anything more and just return
            preferences = read_json("preferences", username)
            if "8. Completion_ticks" in preferences:
                if "8a. Yes/No" in preferences["8. Completion_ticks"]:
                    if preferences["8. Completion_ticks"]["8a. Yes/No"] == "no":
                        return
                if "8c. Days_per_deletion_of_ticked_items" not in preferences["8. Completion_ticks"]:
                    return
            else:
                return # can't do anything if the user hasn't specified preferences about ticked items and their deletion yet
            
            # if a previous check has been done on this user, check user's cache for time of last ticked item deletion
            usercache = read_json("usercache", username)
            days_per_deletion_of_ticked_items = int(preferences["8. Completion_ticks"]["8c. Days_per_deletion_of_ticked_items"])
            if "Last_ticked_item_deletion_UTC" in usercache:
                Last_ticked_item_deletion_UTC = usercache["Last_ticked_item_deletion_UTC"]
                Last_ticked_item_deletion_UTC = datetime.datetime.strptime(Last_ticked_item_deletion_UTC, "%m/%d/%Y, %H:%M:%S")
                if (now_utc - Last_ticked_item_deletion_UTC).days >= days_per_deletion_of_ticked_items:
                    await self.delete_ticked_items(username)

            # else calculate the number of days since this user's preferred start of the week and see if it matches their "8c. Days_per_deletion_of_ticked_items" pref
            # and cache the time of last deletion (or this user's preferred start of the week if no deletion yet) for this user as a datetime string
            else:
                start_of_week = ""
                days_since_start_of_week = 0
                if "5. Start_of_week" in preferences:
                    start_of_week = preferences["5. Start_of_week"]
                    if start_of_week == "Mon":
                        days_since_start_of_week = now_local.weekday() # weekday() returns the number of days since last Monday
                        last_monday_utc = now_utc - datetime.timedelta(days=now_utc.weekday())
                        usercache["Last_ticked_item_deletion_UTC"] = last_monday_utc.strftime("%m/%d/%Y, %H:%M:%S")
                    else:
                        days_since_start_of_week = now_local.weekday() + 1
                        last_sunday_utc = now_utc - datetime.timedelta(days=now_utc.weekday()+1)
                        usercache["Last_ticked_item_deletion_UTC"] = last_sunday_utc.strftime("%m/%d/%Y, %H:%M:%S")
                    write_json("usercache", username, usercache)
                else:
                    return # can't do anything if the user hasn't specified a preferred start of the week yet

                if days_since_start_of_week == days_per_deletion_of_ticked_items:
                    await self.delete_ticked_items(username)

    
    #########################################################################################
    # every 8 minutes (coprime to 15 which is the smallest real-life unit of timezone offset)
    # check if any preferences file has been modified (or created) in the past 8 minutes and call update() on that file
    # since coprime means that intervals of 8 and 15 minutes will never coincide
    # this avoids race conditions where check_ticked_item_deletion() is called before new users/timezone prefs are registered
    @tasks.loop(minutes=8)
    async def check_updated_prefs(self):
        for file in os.listdir("./jsons/preferences"):
            if time.mktime(datetime.datetime.now().timetuple()) - os.path.getmtime("./jsons/preferences/" + file) <= 480.0: # check difference in time using Unix epoch
                await self.update(file)


######################################################################################################################################################
#                                                                  HELPER FUNCTIONS                                                                  #
######################################################################################################################################################


    #####################
    def update_all(self):
        for file in os.listdir("./jsons/preferences"):
            global times
            username = os.path.splitext(file)[0]
            preferences = read_json("preferences", username)

            if "1. Timezone" in preferences.keys():
                # delete old time in times to replace with new
                if username in self.users_offsets:
                    old_hours, old_minutes = self.users_offsets[username]
                    times.remove(datetime.time(hour=old_hours, minute=old_minutes, tzinfo=datetime.timezone.utc))

                tzdisplaystr = preferences["1. Timezone"]
                hours, minutes = tzdisplaystr_to_24int(tzdisplaystr)
                self.users_offsets[username] = (hours, minutes)
                times.append(datetime.time(hour=hours, minute=minutes, tzinfo=datetime.timezone.utc))
        
        # update the times in @tasks.loop() for check_ticked_item_deletion()
        self.check_ticked_item_deletion.change_interval(time=times)
    

    #################################
    async def update(self, file:str):
        global times
        username = os.path.splitext(file)[0]
        preferences = read_json("preferences", username)

        if "1. Timezone" in preferences.keys():
            # delete old time in times to replace with new
            if username in self.users_offsets:
                old_hours, old_minutes = self.users_offsets[username]
                times.remove(datetime.time(hour=old_hours, minute=old_minutes, tzinfo=datetime.timezone.utc))
                
            tzdisplaystr = preferences["1. Timezone"]
            hours, minutes = tzdisplaystr_to_24int(tzdisplaystr)
            self.users_offsets[username] = (hours, minutes)
            times.append(datetime.time(hour=hours, minute=minutes, tzinfo=datetime.timezone.utc))

            # update the times in @tasks.loop() for check_ticked_item_deletion()
            self.check_ticked_item_deletion.change_interval(time=times)
    

    ##################################################
    async def delete_ticked_items(self, username:str):
        print("ticked items deleted for ", username)

        # cache last ticked item deletion in UTC time (to avoid timezone switch issues etc.)
        usercache = read_json("usercache", username)
        usercache["Last_ticked_item_deletion_UTC"] = datetime.datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
        write_json("usercache", username, usercache)
        pass
    
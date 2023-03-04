import os
import json


# for reading and writing to user preference jsons
# this bot uses the super non-expandable method of storing user preferences as local json files which probably also violates multiple principles of security
# but I'm not planning to expand this widely anyways
def read_JSON(author):
        filepath = f"jsons/{author}.json"
        if os.path.isfile(filepath) and os.stat(filepath).st_size > 0: # if file exists and is not empty
            with open(filepath, "r") as infile: # read from file
                return json.load(infile)
        else:
            open(filepath, "a+") # a+ mode creates the file if it doesn't exist
            return dict()
        
        
def write_JSON(author, prefs):
        with open(f"jsons/{author}.json", "w+") as outfile:
            json.dump(prefs, outfile, indent=2)

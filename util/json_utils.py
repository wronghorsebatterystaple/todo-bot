import os
import json
from collections import OrderedDict


# for reading and writing to jsons
# this bot uses the super non-expandable method of storing user preferences, todo lists, and cache as local, plaintext json files which probably also violates multiple principles of security
# but I'm not planning to expand this widely anyways
def read_json(json_type:str, author:str):
    filepath = f"jsons/{json_type}/{author}.json"
    if os.path.isfile(filepath) and os.stat(filepath).st_size > 0: # if file exists and is not empty
            with open(filepath, "r") as infile: # read from file
                return json.load(infile)
    else:
        open(filepath, "a+") # a+ mode creates the file if it doesn't exist
        return dict()
        
        
def write_json(json_type:str, author:str, dictionary:dict):
    with open(f"jsons/{json_type}/{author}.json", "w+") as outfile:
        json.dump(dictionary, outfile, indent=2)

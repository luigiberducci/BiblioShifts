# File:     main.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import sys
import os
from DoodleParser import DoodleParser
from Solver import Solver

CONFIG_FILE = "config.in"
CONF = dict()

def validate_value(n):
    try:
        n = int(n)
    except ValueError:
        n = ""
    if n == "" or n < 0:
        print("Error: input \"{}\" not valid.".format(n))
        exit(1)
    return n

def parse_config_file(configFile):
    """
    Extract variables from the config file given as input.

    Parameters:
    -----------
        - `configFile` is the config file
    """
    with open(configFile, 'r') as config:
        for line in config.readlines():
            if line[0]=='#':        # Skip commented lines
                continue

            split = line.replace("\n", "").replace("\"","").split("=")
            if len(split)==1:       # Skip empty lines
                continue

            if split[0]=="PROB_NAME":
                CONF["name"] = split[1]
            elif split[0]=="OPLRUN":
                CONF["oplrun"] = split[1]
            elif split[0]=="OUT_DIR":
                CONF["out_dir"] = split[1]
            elif split[0]=="MOD_DIR":
                CONF["model_dir"] = split[1]
            elif split[0]=="DATA_DIR":
                CONF["data_dir"] = split[1]
            elif split[0]=="MOD_PROB_1":
                CONF["model_file"] = split[1]
            elif split[0]=="DATA_PROB_1":
                CONF["data_file"] = split[1]
            elif split[0]=="OUT_PROB_1":
                CONF["out_file"] = split[1]
            else:
                pass

def ask_for_min_max_shifts(participants):
    """
    Asks the user to specify the minimum number of shifts to assign to each user.
    """
    minMaxShifts = dict()
    for p in participants:
        n = input("Min and max number of shifts to assign to {} (format: 'min,max' or just 'min')? ".format(p)).split(',')
        if len(n) == 1:
            if n[0] == "":
                minMaxShifts[p] = (None, None)
            else:
                minMaxShifts[p] = (validate_value(n[0]), None)
        else:
            minMaxShifts[p] = (validate_value(n[0]), validate_value(n[1]))
    return minMaxShifts

if __name__=="__main__":
    if len(sys.argv)<2:
        print("[Error] Invalid number of arguments.")
        print("\tUsage: python3 {} <pollID>".format(sys.argv[0]))
        exit(1)

    pollID = sys.argv[1]
    parse_config_file(CONFIG_FILE)

    parser = DoodleParser(pollID)

    numMinMaxShifts = ask_for_min_max_shifts(parser.get_participants())

    solver = Solver(CONF["name"])
    solver.set_opl_exe(CONF["oplrun"])
    solver.set_model(os.path.join(CONF["model_dir"], CONF["model_file"]))
    solver.set_data(os.path.join(CONF["data_dir"], CONF["data_file"]))
    solver.set_output_file(os.path.join(CONF["out_dir"], CONF["out_file"]))

    solver.config_problem(parser.get_participants(),
                          parser.get_options(),
                          parser.get_calendar(),
                          numMinMaxShifts)

    print("Run solver")
    solver.solve()

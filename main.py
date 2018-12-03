# File:     main.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import sys
import os
import xlsxwriter
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

def write_result_to_excel(result, output_file, problem_name):
    """
    Write the result in an Excel file.

    Parameters:
    -----------
        -`result` a dict of dicts with structure day->shift->student
        -`output_file` is the filename of output file
    """
    # Drawing parameters
    interline  = 1
    offset_inc = 3

    columns = ["B", "C", "D", "E", "F", "G", "H"]
    days    = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    skip_days = ["Sat", "Sun"]

    rows    = ["1", "2", "3"]
    shifts  = ["09:30", "12:30", "15:30"]

    offset = 1
    first_occurrence = True

    my_workbook  = xlsxwriter.Workbook(output_file)
    my_worksheet = my_workbook.add_worksheet()

    # Header
    my_worksheet.write("A1", "Automatic assignment for {}".format(problem_name))
    offset = offset + 1
    for dd, cc in zip(days, columns):
        if dd in skip_days:
            continue
        my_worksheet.write( cc+str(offset), dd)
    offset = offset + 1

    for k, d in enumerate(result.keys()):
        if d[0:3] in skip_days:
            continue
        if d.startswith("Mon") and first_occurrence:
            first_occurrence = False
            if k != 0:  # No increment on first week
                offset = offset + offset_inc + interline

            date = int(d.split(" ")[1])
            for cc in columns:
                if cc in [columns[days.index(d)] for d in skip_days]:
                    continue
                my_worksheet.write( cc+str(offset), date )
                date = date + 1
            for rr in rows:
                my_worksheet.write( "A"+str(offset+int(rr)), shifts[rows.index(rr)] )


        if d.startswith("Fri"):
            first_occurrence = True

        for k, t in enumerate(result.get(d)):
            student = result.get(d).get(t)

            current_col = columns[ days.index(d[0:3]) ]
            current_row = str(offset + int(t))

            print("Day {} - Shift {} -> {} | {}{}".format(d, t, student, current_col, current_row))

            my_worksheet.write( current_col+current_row, student )


    my_workbook.close()

if __name__=="__main__":
    if len(sys.argv)<2:
        print("[Error] Invalid number of arguments.")
        print("\tUsage: python3 {} <pollID> [offline]".format(sys.argv[0]))
        exit(1)
    elif len(sys.argv)>2:
        if sys.argv[2]=="offline":
            offline = True
    else:
        offline = False

    # Take the input arguments and the data from config file
    pollID = sys.argv[1]
    parse_config_file(CONFIG_FILE)
    output_filepath = os.path.join(CONF["out_dir"], CONF["out_file"])
    model_filepath = os.path.join(CONF["model_dir"], CONF["model_file"])
    data_filepath = os.path.join(CONF["data_dir"], CONF["data_file"])

    if not(offline):
        # Parse the doodle survey
        parser = DoodleParser(pollID)

        # Ask to the user to specify the min, max number of shifts for each participant
        numMinMaxShifts = ask_for_min_max_shifts(parser.get_participants())

    # Create the solver
    solver = Solver(CONF["name"])

    # Configure the solver
    solver.set_opl_exe(CONF["oplrun"])
    solver.set_model(model_filepath)
    solver.set_data(data_filepath)
    solver.set_output_file(output_filepath)

    if not(offline):
        # Configure the problem and set data for participants, options, preferences and shifts
        solver.config_problem(parser.get_participants(),
                              parser.get_options(),
                              parser.get_calendar(),
                              numMinMaxShifts)

    # Run the solver
    result = solver.solve()

    # Save result
    write_result_to_excel(result, output_filepath, CONF["name"])

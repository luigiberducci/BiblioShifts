# File:     main.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import argparse
import sys
import os
import xlsxwriter
import time
from DoodleParser import DoodleParser
from Solver import Solver

CONFIG_FILE = "config.in"
CONF = dict()

def error(string):
    """ Print error message.

    Parameters:
    -----------
        -`string` the message content
    """
    print("[Error] {}".format(string))

def info(string):
    """ Print info message.

    Parameters:
    -----------
        -`string` the message content
    """
    print("[Info] {}".format(string))

def validate_value(n):
    try:
        n = int(n)
    except ValueError:
        n = ""
    if n == "" or n < 0:
        error("input \"{}\" not valid.".format(n))
        exit(1)
    return n

def get_all_shifts(calendar):
    """
    Return a sorted set containing all the shifts which may occur in a single day.
    """
    shift_names = set()
    for k, d in enumerate(calendar.keys()):
        for k, t in enumerate(calendar.get(d).keys()):
            shift_names.add(t)
    return sorted(shift_names)


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
            elif split[0]=="MOD_PROB_2":
                CONF["model_file_min_trips"] = split[1]
            elif split[0]=="DATA_PROB_2":
                CONF["data_file_min_trips"] = split[1]
            elif split[0]=="OUT_PROB_2":
                CONF["out_file_min_trips"] = split[1]
            else:
                pass

def ask_for_max_shifts_per_day():
    """
    Asks to user to specify the maximum number of shifts to assign to the same student in a day.

    Returns:
    --------
        -`maxShiftsXDay` is and integer
    """
    maxShiftsXDay = 1
    n = input(" $> Max number of shifts to assign to a student in the same day? (format: 'val', by default is 1)")
    if n!="":
        maxShiftsXDay = validate_value(n)
    return maxShiftsXDay

def ask_for_min_max_shifts(participants):
    """
    Asks the user to specify the minimum number of shifts to assign to each user.
    """
    minMaxShifts = dict()
    for p in participants:
        n = input(" $> Min and max number of shifts to assign to {} (format: 'min,max' or just 'min')? ".format(p)).split(',')
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
        -`result` a dict which maps day->list, where:
                    -`day` is the string identifier for a day
                    -`list` is a dict which maps shift->student, where:
                        -`shift` is the string identifier of shift
                        -`student` is the name of the student assigned to `shift` in `day`
        -`output_file` is the filename of output file
        -`problem_name` is a string which names the problem, for printing purposes
    """
    # Drawing parameters
    interline  = 1
    offset_inc = 3
    inter_table_summary = 3

    columns   = ["B", "C", "D", "E", "F"]
    i_columns = [ 1,   2,   3,   4,   5 ]
    days      = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    shifts  = get_all_shifts(result)

    offset = 1
    first_occurrence = True

    # XlsxWriter creation and formats
    my_workbook  = xlsxwriter.Workbook(output_file)
    my_worksheet = my_workbook.add_worksheet(problem_name)
    default_fmt  = my_workbook.add_format()
    centered_fmt = my_workbook.add_format({'align':'center', 'valign':'vcenter'})
    bold_cnt_fmt = my_workbook.add_format({'bold':1, 'align':'center', 'valign':'vcenter'})

    # Preliminary setup
    max_lenght = 0              # Max lenght of student name
    for d in result.keys():
        for t in result.get(d):
            lenght = len(result.get(d).get(t))
            max_lenght = max(max_lenght, lenght)
    # Set column width and merge first cells for title
    my_worksheet.set_column(0, 0, max_lenght, default_fmt)
    my_worksheet.set_column(i_columns[0], i_columns[-1], max_lenght, centered_fmt)
    my_worksheet.merge_range("A1:{}1".format(columns[-1]), "", centered_fmt)

    # Header
    my_worksheet.write("A1", "Automatic assignment for {}".format(problem_name), bold_cnt_fmt)
    offset = offset + 1
    for dd, cc in zip(days, columns):
        my_worksheet.write( "{}{}".format(cc, str(offset)), dd, bold_cnt_fmt)
    offset = offset + 1

    # Loop on lines
    students_stat = dict()  # Shifts-assigned counter for statistics
    for k, d in enumerate(result.keys()):
        if d.startswith("Mon") and first_occurrence:
            first_occurrence = False
            if k != 0:  # No increment on first week
                offset = offset + offset_inc + interline

            date = int(d.split(" ")[1])
            for cc in columns:
                if date > 31:
                    break
                my_worksheet.write( "{}{}".format(cc, str(offset)), date, bold_cnt_fmt)
                date = date + 1
            for rr, t in enumerate(shifts):
                my_worksheet.write( "A{}".format(str(offset+rr+1)), t, bold_cnt_fmt)

        if d.startswith("Fri"):
            first_occurrence = True

        for k, t in enumerate(result.get(d)):
            student = result.get(d).get(t)
            if students_stat.get(student)==None: # Eventually initialize counter
                students_stat[student] = 0
            students_stat[student] = students_stat.get(student) + 1 # Increment counter

            current_col = columns[ days.index(d[0:3]) ]
            current_row = str(offset + shifts.index(t) + 1)

            my_worksheet.write( "{}{}".format(current_col, current_row), student )

    # Write summary
    offset = int(current_row) + inter_table_summary
    my_worksheet.write( "A{}".format(str(offset)), "Student", bold_cnt_fmt)
    my_worksheet.write( "B{}".format(str(offset)), "Nr. Shifts", bold_cnt_fmt)
    offset = offset + 1
    for i,s in enumerate(students_stat.keys()):
        current_row = str(offset + i)
        current_col = "A"
        my_worksheet.write( "{}{}".format(current_col, current_row), s)

        current_col = "B"
        my_worksheet.write( "{}{}".format(current_col, current_row), students_stat.get(s))


    my_workbook.close()

def run_all_process(problem_name, model_filepath, data_filepath, output_filepath, offline, opl_exe_path, parser):
    """
    Run the entire process: Doodle parsing, run the solver and output writing.

    Parameters:
    -----------
        -`problem_name` is the string identifier for the current problem
        -`model_filepath` is the path to the mod file
        -`data_filepath` is the path to the dat file
        -`output_filepath` is the path to the output file (create it or overwrite)
        -`offline` is a boolean flag to enable the new data creation or use the existing one
        -`opl_exe_path` is the path to the OPL executable
        -`parser` is the DoodleParser object which collects info on participants, calendar, ...
    """
    assert(problem_name),    "Problem name is not defined"
    assert(model_filepath),  "Model file not defined"
    assert(data_filepath),   "Data file not defined"
    assert(output_filepath), "Output file not defined"
    assert(opl_exe_path),    "OPL exe not defined"
    assert(not(offline) or parser==None), "Offline/Parser inconsistency"    # if offline then parser==None
    assert(offline or parser!=None),      "Offline/Parser inconsistency"    # if not(offline) then parser!=None

    info("Initial configuration...\tDONE")

    if not(offline) and parser!=None:
        # Ask to the user to specify the min, max number of shifts for each participant
        numMinMaxShifts = ask_for_min_max_shifts(parser.get_participants())
        numMaxShiftsPerDay = ask_for_max_shifts_per_day()

    # Create the solver
    solver = Solver(problem_name)

    # Configure the solver
    solver.set_opl_exe(opl_exe_path)
    solver.set_model(model_filepath)
    solver.set_data(data_filepath)
    solver.set_output_file(output_filepath)

    if not(offline) and parser!=None:
        # Configure the problem and set data for participants, options, preferences and shifts
        solver.config_problem(parser.get_participants(),
                              parser.get_options(),
                              parser.get_calendar(),
                              numMinMaxShifts, numMaxShiftsPerDay)

    info("Configure Solver...\tDONE\n")
    info("Run the solver!\n")

    # Take init solve time
    ts0 = time.time()
    # Run the solver
    opt_val, result = solver.solve()
    # Take final solve time
    tsf = time.time()

    if opt_val==None or result == "":   # Something goes wrong in solving
        error("The problem has no solution.\n")
    else:
        info("Objective function: {}".format(opt_val))
        info("Write Excel result in {}...\n".format(output_filepath))

        # Save result
        write_result_to_excel(result, output_filepath, CONF["name"])

    # Print statistic info about elapsed time
    info("Solver spent \t{0:.{digits}f} seconds.".format((tsf-ts0), digits=3))

if __name__=="__main__":
    # Default parameters' assignment
    execProblem1 = True
    execProblem2 = True
    offline      = False

    # Retrieve input arguments
    argParser = argparse.ArgumentParser()

    argParser.add_argument("pollID",    help="poll identifier, take it from the Doodle link")
    argParser.add_argument("--offline", help="no access to Doodle, use the existing dat file", action="store_true")
    argParser.add_argument("--problem", help="select the problem you want to solve", type=int)

    args =  argParser.parse_args()

    if args.offline==True:
        offline = True
    if args.problem==1:
        execProblem1 = True
        execProblem2 = False
    elif args.problem==2:
        execProblem1 = False
        execProblem2 = True

    # Take init time, for statistics purposes
    t0 = time.time()

    # Take the input arguments and the data from config file
    pollID = sys.argv[1]
    parse_config_file(CONFIG_FILE)

    # Retrieve global information from config file
    problem_name = CONF["name"]
    opl_exe_path = CONF["oplrun"]

    # Doodle Parsing
    if not(offline):
        # Parse the doodle survey
        parser = DoodleParser(pollID)
        info("Parsing Doodle...\tDONE")
    else:
        parser = None

    # PROBLEM 1 : Balanced distribution
    if(execProblem1):
        output_filepath = os.path.join(CONF["out_dir"],   CONF["out_file"])
        model_filepath  = os.path.join(CONF["model_dir"], CONF["model_file"])
        data_filepath   = os.path.join(CONF["data_dir"],  CONF["data_file"])
        # Start the solving of PROBLEM 1
        run_all_process(problem_name, model_filepath, data_filepath, output_filepath, offline, opl_exe_path, parser)

    # PROBLEM 2 : Minimize trips
    if(execProblem2):
        output_filepath = os.path.join(CONF["out_dir"],   CONF["out_file_min_trips"])
        model_filepath  = os.path.join(CONF["model_dir"], CONF["model_file_min_trips"])
        data_filepath   = os.path.join(CONF["data_dir"],  CONF["data_file_min_trips"])
        # Start the solving of PROBLEM 2
        run_all_process(problem_name, model_filepath, data_filepath, output_filepath, offline, opl_exe_path, parser)

    tf = time.time()
    info("Program ends in \t{0:.{digits}f} seconds.".format((tf-t0), digits=3))

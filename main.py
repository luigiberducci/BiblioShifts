# File:     main.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

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
        error("Error: input \"{}\" not valid.".format(n))
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

    rows    = ["1", "2", "3"]
    shifts  = ["09:30", "12:30", "15:30"]

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
            for rr in rows:
                my_worksheet.write( "A{}".format(str(offset+int(rr))), shifts[rows.index(rr)], bold_cnt_fmt)


        if d.startswith("Fri"):
            first_occurrence = True

        for k, t in enumerate(result.get(d)):
            student = result.get(d).get(t)
            if students_stat.get(student)==None: # Eventually initialize counter
                students_stat[student] = 0
            students_stat[student] = students_stat.get(student) + 1 # Increment counter

            current_col = columns[ days.index(d[0:3]) ]
            current_row = str(offset + int(t))

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

if __name__=="__main__":
    if len(sys.argv)<2:
        error("Invalid number of arguments.\n" +
              "\tUsage: python3 {} <pollID> [offline]".format(sys.argv[0]))
        exit(1)
    elif len(sys.argv)>2:
        if sys.argv[2]=="offline":
            offline = True
    else:
        offline = False

    # Take init time, for statistics purposes
    t0 = time.time()

    # Take the input arguments and the data from config file
    pollID = sys.argv[1]
    parse_config_file(CONFIG_FILE)
    output_filepath = os.path.join(CONF["out_dir"], CONF["out_file"])
    model_filepath = os.path.join(CONF["model_dir"], CONF["model_file"])
    data_filepath = os.path.join(CONF["data_dir"], CONF["data_file"])

    info("Initial configuration...\tDONE")

    if not(offline):
        # Parse the doodle survey
        parser = DoodleParser(pollID)

        info("Parsing Doodle...\tDONE")

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

    info("Configure Solver...\tDONE\n")
    info("Run the solver!")

    # Take init solve time
    ts0 = time.time()
    # Run the solver
    result = solver.solve()
    # Take final solve time
    tsf = time.time()

    info("Write the result to Excel...\n")

    # Save result
    write_result_to_excel(result, output_filepath, CONF["name"])

    # Take final time
    tf = time.time()
    info("Solver spent \t{0:.{digits}f} seconds.".format((tsf-ts0), digits=3))
    info("Program ends in \t{0:.{digits}f} seconds.".format((tf-t0), digits=3))
    info("You can find the result in {}".format(output_filepath))

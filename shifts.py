"""
Author: Cristian Di Pietrantonio.
Author: Luigi Berducci.
"""
import json
import requests
import datetime
import sys



def parse_doodle(pollID):
    """
    Retrieves poll data from doodle.com given the poll identifier.

    Parameters:
    -----------
        - `pollID`: the poll identifier (get it from the url)

    Returns:
    --------
    a tuple (participants, options, calendar) where
        - `participants` is a mapping userID -> userName
        - `options` is a list of datetime objects, representing the poll options
        - `calendar` is a mapping optionIndex -> list of userID
    """
    JSON = requests.get("https://doodle.com/api/v2.0/polls/" + pollID).content.decode('utf-8')
    JSON = json.loads(JSON)

    options = [ datetime.datetime.fromtimestamp(x['start']/1000)
                for x in JSON['options']]
    options_dict = dict()
    for d in options:
        options_dict[str(d.year) + "-" + str(d.month).zfill(2) + "-" + str(d.day).zfill(2)] = []

    for d in options:
        options_dict[str(d.year) + "-" + str(d.month).zfill(2) + "-" + str(d.day).zfill(2)].append( str(d.hour).zfill(2) + ":" + str(d.minute).zfill(2))

    calendar = dict()
    for d, k in enumerate(options_dict.keys()):
        calendar[k] = dict()
        for t, l in enumerate(options_dict.get(k)):
            calendar[k][l] = list()

    participants = dict()
    emptyShiftCounter = 0
    for participant in JSON['participants']:
        pID = participant['id']
        pName = participant['name']
        participants[pID] = pName

        for i, pref in enumerate(participant['preferences']):
            if pref <= 0:
                continue
            k2 = 0
            for d, k in enumerate(options_dict.keys()):
                for t, l in enumerate(options_dict.get(k)):
                    if k2==i:
                        calendar[k][l].append(pID)
                    k2 = k2+1

    for k in calendar:
        if len(calendar[k]) == 0:
            emptyShiftCounter += 1
            # calendar[k].append(-emptyShiftCounter) # empty shift
            # participants[-emptyShiftCounter] = "<vuoto>"

    return participants, options, options_dict, calendar



def format_date(date):
    """
    Returns a string representation of `date` datetime object, for printing purposes.
    """
    return "{}/{}/{} {}:{}".format(date.day, date.month, date.year, date.hour, date.minute)



def format_solution(solution, participants, options):
    """
    Return a string representation of the solution.
    """
    text = "Shifts:\n_______\n\n"
    for i, option in enumerate(options):
        text += "{}   -->  {}\n".format(format_date(option), participants[solution[i]])
    return text


def validate_value(n):
    try:
        n = int(n)
    except ValueError:
        n = ""
    if n == "" or n < 0:
        print("Error: input \"{}\" not valid.".format(n))
        exit(1)
    return n

def ask_for_min_max_shifts(participants):
    """
    Asks the user to specify the minimum number of shifts to assign to each user.
    """
    minMaxShifts = dict()
    for p in participants:
        if p >= 0:
            n = input("Min and max number of shifts to assign to {} (format: 'min,max' or just 'min')? ".format(participants[p])).split(',')
            if len(n) == 1:
                if n[0] == "":
                    minMaxShifts[p] = (None, None)
                else:
                    minMaxShifts[p] = (validate_value(n[0]), None)
            else:
                minMaxShifts[p] = (validate_value(n[0]), validate_value(n[1]))
    return minMaxShifts

def solve_with_constraints_lib(participants, options, calendar, partToMinShifts):
    """
    Formulate and solve the problem using `constraint` library

    Parameters:
    -----------
        - `participants`: mapping participantID -> participantName
        - `options`: list of datetime objects
        - `calendar`: mapping optionID -> list of participantID
        - `partToMinShifts`: mapping paricipantID -> min number of shifts to be assigned
    """
    turni = Problem(MinConflictsSolver(1000000))
    for k in calendar:
        turni.addVariable(k, calendar[k])

    empty_shift = lambda x: x[0] < 0
    # Constraint 1 - maximum one shift per person per day
    slotsInSameDay = list() if empty_shift(calendar[0]) else [0]
    for i in range(1, len(options)):
        if empty_shift(calendar[i]):
            continue
        elif options[i].day == options[i-1].day:
            slotsInSameDay.append(i)
        elif len(slotsInSameDay) > 1:
            # add all different constraints
            turni.addConstraint(AllDifferentConstraint(), slotsInSameDay)
            slotsInSameDay = [i]

    if len(slotsInSameDay) > 1:
        # add all different constraints
        turni.addConstraint(AllDifferentConstraint(), slotsInSameDay)

    # Constraint 2 - each person p is assigned with at least partToMinShifts[p] shifts
    for k in partToMinShifts:
        if k < 0:
            continue
        minVal, maxVal = partToMinShifts[k]
        turni.addConstraint(MinimumValueFrequency(k, minVal, sum([partToMinShifts[g][0] for g in partToMinShifts if g != k])))
        if maxVal is not None:
            turni.addConstraint(MaximumValueFrequency(k, maxVal))
    solution = turni.getSolution()
    if solution is None:
        print("No solution found. Try again.")
        exit()
    textSol = format_solution(solution, participants, options)
    print(textSol)



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: shifts.py <doodle-poll-id>")
        exit(1)

    pollID = sys.argv[1]
    participants, options, options_dict, calendar = parse_doodle(pollID)

    # sys.stdout.write("**********************************************\n")
    # sys.stdout.write("               PARTICIPANTS\n")
    # sys.stdout.write("**********************************************\n")
    # for k,i in enumerate(participants.keys()):
    #     if k==0:
    #         sys.stdout.write(participants.get(i))
    #     else:
    #         sys.stdout.write(", " + participants.get(i))

    # sys.stdout.write("\n\n")
    # sys.stdout.write("**********************************************\n")
    # sys.stdout.write("              LIST OPTIONS\n")
    # sys.stdout.write("**********************************************\n")
    # for k,d in enumerate(options):
    #     if k==0:
    #         sys.stdout.write(str(d))
    #     else:
    #         sys.stdout.write(", " + str(d))

    # sys.stdout.write("\n\n")
    # sys.stdout.write("**********************************************\n")
    # sys.stdout.write("                   CALENDAR\n")
    # sys.stdout.write("**********************************************\n")
    # sys.stdout.write("    DAY    :   SLOT    ->    PARTICIPANTS\n")
    # sys.stdout.write("**********************************************\n")
    shift_names = set()
    for k, d in enumerate(calendar.keys()):
        for k, t in enumerate(calendar.get(d).keys()):
            shift_names.add(t)
    shift_names = sorted(shift_names)

    # Ask to the user the minimum number of shifts
    partToMinShifts = ask_for_min_max_shifts(participants)

    # Print the file .dat for CPLEX
    # Compute the maximum number of shifts in a day, among all days
    max_daily_shifts = len(shift_names)
    max_num_shifts = max_daily_shifts * len(options_dict.keys())
    outFilepath = "output.txt"
    out = ""

    # Header
    out += "/*********************************************\n"
    out += " * OPL 12.8.0.0 Data\n"
    out += " * Author: Luigi Berducci\n"
    out += " * Creation Date: {}\n".format(datetime.date.today())
    out += " *********************************************/\n"
    out += "\n"

    # Parameters
    out += "/* Define the parameters */\n"
    out += "numStudents = {};\n".format(len(participants))
    out += "numDays     = {};\n".format(len(options_dict.keys()))
    out += "numShifts   = {};\n".format(max_daily_shifts)
    out += "\n"

    # Output file
    out += "/* Define the output file */\n"
    out += "outFilepath = \"{}\";\n".format(outFilepath)
    out += "\n"

    # Student names
    out += "/* Define the student names */\n"
    out += "StudNames = #[\n"
    for k, p_id in enumerate(participants.keys()):
        if k == len(participants.keys())-1:
            out += "    {}: \"{}\"\n".format(k+1, participants.get(p_id))
        else:
            out += "    {}: \"{}\",\n".format(k+1, participants.get(p_id))
    out += "]#;\n"
    out += "\n"

    # Day names
    out += "/* Define the day names */\n"
    out += "DayNames = #[\n"
    for k, d_name in enumerate(options_dict.keys()):
        if k == len(options_dict.keys())-1:
            out += "    {}: \"{}\"\n".format(k+1, d_name)
        else:
            out += "    {}: \"{}\",\n".format(k+1, d_name)
    out += "]#;\n"
    out += "\n"

    # Existance of shifts
    num_existing_shifts = 0
    out += "/* Define the existing shifts */\n"
    out += "Existance = #[\n"
    for k, d_name in enumerate(options_dict.keys()):
        string_array = []
        for kk, s_name in enumerate(shift_names):
            if s_name in options_dict.get(d_name):
                string_array.append(1)
                num_existing_shifts = num_existing_shifts + 1
            else:
                string_array.append(0)
        if k == len(options_dict.keys())-1:
            out += "    {}: {}\n".format(k+1, str(string_array))
        else:
            out += "    {}: {},\n".format(k+1, str(string_array))
    out += "]#;"
    out += "\n"

    # Availability of students
    out += "/* Define students availability */\n"
    out += "Availability = [\n"
    for k, p_id in enumerate(participants.keys()):
        out += "    #[    /* {} */\n".format(participants.get(p_id))
        for kk, d_name in enumerate(options_dict.keys()):
            string_array = []
            for kkk, s_name in enumerate(shift_names):
                if calendar.get(d_name).get(s_name)!=None and p_id in calendar.get(d_name).get(s_name):
                    string_array.append(1)
                else:
                    string_array.append(0)
            if kk == len(options_dict.keys())-1:
                out += "        {}:    {}    /* {} */\n".format(kk+1, str(string_array), d_name)
            else:
                out += "        {}:    {},   /* {} */\n".format(kk+1, str(string_array), d_name)
        if k == len(participants.keys())-1:
            out += "     ]#\n"
        else:
            out += "     ]#,\n"
    out += "];\n"
    out += "\n"

    # Minimum number of shifts for each students
    out += "/* Define the minimum number of shifts to assign at students */\n"
    out += "MinNumShifts = #[\n"
    for k, p_id in enumerate(partToMinShifts):
        if partToMinShifts.get(p_id)[0] == None:
            partToMinShifts[p_id] = (num_existing_shifts//len(participants), partToMinShifts.get(p_id)[1])
        if k == len(partToMinShifts)-1:
            out += "    {}: {}\n".format(k+1, partToMinShifts.get(p_id)[0])
        else:
            out += "    {}: {},\n".format(k+1, partToMinShifts.get(p_id)[0])
    out += "]#;\n"
    out += "\n"

    # Maximum number of shifts for each students
    out += "/* Define the max number of shifts to assign at students */\n"
    out += "MaxNumShifts = #[\n"
    for k, p_id in enumerate(partToMinShifts):
        if partToMinShifts.get(p_id)[1] == None:
            partToMinShifts[p_id] = (partToMinShifts.get(p_id)[0], max_num_shifts)
        if k == len(partToMinShifts)-1:
            out += "    {}: {}\n".format(k+1, partToMinShifts.get(p_id)[1])
        else:
            out += "    {}: {},\n".format(k+1, partToMinShifts.get(p_id)[1])
    out += "]#;\n"
    out += "\n"



    # Write to output file
    with open("test.dat", 'w') as f:
        f.write(out)
    # create CSP problem
    # solve_with_constraints_lib(participants, options, calendar, partToMinShifts)

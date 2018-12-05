# File:     Solver.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import sys
import subprocess
from subprocess import Popen, PIPE
import datetime

class Solver:
    """
    Configure problem in OPL and solve it using OPLrun executable.
    """
    opl_exe      = ""
    problem      = ""
    data_content = ""
    model_file   = ""
    data_file    = ""
    output_file  = ""
    result       = ""

    def __init__(self, probName):
        """
        Build the Solver object.

        Parameters:
        -----------
            - `probName` is the problem string identifier
        """
        self.problem = probName

    def set_opl_exe(self, oplExecutable):
        """
        Set the opl executable filepath.

        Parameters:
        -----------
            - `oplExecutable` is the new filepath
        """
        self.opl_exe = oplExecutable


    def set_model(self, modelPath):
        """
        Set the model filepath.

        Parameters:
        -----------
            - `modelPath` is the new filepath
        """
        self.model_file = modelPath

    def set_data(self, dataPath):
        """
        Set the data filepath.

        Parameters:
        -----------
            - `dataPath` is the new filepath
        """
        self.data_file = dataPath

    def set_output_file(self, outputPath):
        """
        Set the output filepath.

        Parameters:
        -----------
            - `outputPath` is the new filepath
        """
        self.output_file = outputPath

    def config_problem(self, participants, options, calendar, minMaxShifts, maxShiftsPerDay):
        """
        Create a data file according to the given input.

        Parameters:
        -----------
            - `participants` is the list of users who participate to the doodle survey
            - `options` is a dict which map day->list, where
                - `day` is a date
                - `list` is the collection of shifts in `day`
            - `calendar` is a dict which map day->pref, where
                - `day` is a date
                - `pref` is a dict which map shift->part, where
                    - `shift` is a shift in `day`
                    - `part` is a list of participants which express `shift` as preference
        """
        all_shifts = get_all_shifts(calendar)

        # Header
        self.data_content += "/*********************************************\n"
        self.data_content += " * Name: {}\n".format(self.problem)
        self.data_content += " * This file is generated automatically\n"
        self.data_content += " *\n"
        self.data_content += " * Creation Date: {}\n".format(datetime.date.today())
        self.data_content += " *********************************************/\n"
        self.data_content += "\n"

        # Parameters
        self.data_content += "/* Define the parameters */\n"
        self.data_content += "numStudents = {};\n".format(len(participants))
        self.data_content += "numDays     = {};\n".format(len(options.keys()))
        self.data_content += "numShifts   = {};\n".format(len(all_shifts))
        self.data_content += "\n"
        self.data_content += "MaxNumShiftsPerDay = {};\n".format(maxShiftsPerDay)
        self.data_content += "\n"

        # Student names
        self.data_content += "/* Define the student names */\n"
        self.data_content += "StudNames = #[\n"
        for k, p_name in enumerate(participants):
            if k == len(participants)-1:
                self.data_content += "    {}: \"{}\"\n".format(k+1, p_name)
            else:
                self.data_content += "    {}: \"{}\",\n".format(k+1, p_name)
        self.data_content += "]#;\n"
        self.data_content += "\n"

        # Day names
        self.data_content += "/* Define the day names */\n"
        self.data_content += "DayNames = #[\n"
        for k, d_name in enumerate(options.keys()):
            if k == len(options.keys())-1:
                self.data_content += "    {}: \"{}\"\n".format(k+1, d_name)
            else:
                self.data_content += "    {}: \"{}\",\n".format(k+1, d_name)
        self.data_content += "]#;\n"
        self.data_content += "\n"

        # Shift names
        self.data_content += "/* Define the shift names */\n"
        self.data_content += "ShiftNames = #[\n"
        for k, t_name in enumerate(all_shifts):
            if k == len(all_shifts)-1:
                self.data_content += "    {}: \"{}\"\n".format(k+1, t_name)
            else:
                self.data_content += "    {}: \"{}\",\n".format(k+1, t_name)
        self.data_content += "]#;\n"
        self.data_content += "\n"


        # Existance of shifts
        num_existing_shifts = 0
        self.data_content += "/* Define the existing shifts */\n"
        self.data_content += "Existance = #[\n"
        for k, d_name in enumerate(options.keys()):
            string_array = []
            for kk, s_name in enumerate(all_shifts):
                if s_name in options.get(d_name) and len(calendar.get(d_name).get(s_name))>0:
                    string_array.append(1)
                    num_existing_shifts = num_existing_shifts + 1
                else:
                    string_array.append(0)
            if k == len(options.keys())-1:
                self.data_content += "    {}: {}    /* {} */\n".format(k+1, str(string_array), d_name)
            else:
                self.data_content += "    {}: {},   /* {} */\n".format(k+1, str(string_array), d_name)
        self.data_content += "]#;"
        self.data_content += "\n"

        # Availability of students
        self.data_content += "/* Define students availability */\n"
        self.data_content += "Availability = [\n"
        for k, p_name in enumerate(participants):
            self.data_content += "    #[    /* {} */\n".format(p_name)
            for kk, d_name in enumerate(options.keys()):
                string_array = []
                for kkk, s_name in enumerate(all_shifts):
                    if calendar.get(d_name).get(s_name)!=None and p_name in calendar.get(d_name).get(s_name):
                        string_array.append(1)
                    else:
                        string_array.append(0)
                if kk == len(options.keys())-1:
                    self.data_content += "        {}:    {}    /* {} */\n".format(kk+1, str(string_array), d_name)
                else:
                    self.data_content += "        {}:    {},   /* {} */\n".format(kk+1, str(string_array), d_name)
            if k == len(participants)-1:
                self.data_content += "     ]#\n"
            else:
                self.data_content += "     ]#,\n"
        self.data_content += "];\n"
        self.data_content += "\n"

        # Compute the number of free shifts (i.e. the number of shifts that are not required by participants)
        num_remaining_shifts = num_existing_shifts
        for p_id in minMaxShifts.keys():
            if minMaxShifts.get(p_id)[0] == None:
                continue
            num_remaining_shifts = num_remaining_shifts - minMaxShifts.get(p_id)[0]

        # Minimum number of shifts for each students
        self.data_content += "/* Define the minimum number of shifts to assign to students */\n"
        self.data_content += "MinNumShifts = #[\n"
        for k, p in enumerate(minMaxShifts):
            if minMaxShifts.get(p)[0] == None:
                minMaxShifts[p] = (0, minMaxShifts.get(p)[1])
            if k == len(minMaxShifts)-1:
                self.data_content += "    {}: {}    /* {} */\n".format(k+1, minMaxShifts.get(p)[0], p)
            else:
                self.data_content += "    {}: {},   /* {} */\n".format(k+1, minMaxShifts.get(p)[0], p)
        self.data_content += "]#;\n"
        self.data_content += "\n"

        # Maximum number of shifts for each students
        self.data_content += "/* Define the max number of shifts to assign to students */\n"
        self.data_content += "MaxNumShifts = #[\n"
        for k, p in enumerate(minMaxShifts):
            if minMaxShifts.get(p)[1] == None:
                minMaxShifts[p] = (minMaxShifts.get(p)[0], num_existing_shifts)
            if k == len(minMaxShifts)-1:
                self.data_content += "    {}: {}    /* {} */\n".format(k+1, minMaxShifts.get(p)[1], p)
            else:
                self.data_content += "    {}: {},   /* {} */\n".format(k+1, minMaxShifts.get(p)[1], p)
        self.data_content += "]#;\n"
        self.data_content += "\n"

        # If data file defined, write data content
        if self.data_file != "":
            with open(self.data_file, 'w') as dat:
                dat.write(self.data_content)

    def solve(self):
        """
        Run OPLrun executable to solve the problem.
        """
        if self.opl_exe == "" or self.model_file == "" or self.data_file == "":
            return
        # subprocess.call([self.opl_exe, self.model_file, self.data_file])
        p = subprocess.Popen([self.opl_exe, self.model_file, self.data_file], stdout=PIPE)
        out = p.communicate()

        opt_val = None                      # Optimal value initialization
        out_lines = str(out).split("\\n")
        begin = 0                           # Begin line CSV output
        end   = len(out_lines)              # End line CSV output

        for l, line in enumerate(out_lines):
            if "OBJECTIVE" in line:     # Retrieve optimal result of objective function
                opt_val = line.split(": ")[1]
            if "no solution" in line:   # Retrieve unsolvability and eventually break execution
                return None,""
            if "[Info]" in line:    # Retrieve the delimiters lines, discarding the cplex output
                if "Begin output" in line:  # Starting line
                    begin = l
                elif "End output" in line:  # Final line
                    end   = l
                else:
                    continue

        # Initialize result structure
        result = dict()

        # Return the result
        for l, line in enumerate(out_lines[begin+1 : end]):
            if line=="":
                continue
            split_line = line.split(",")

            day     = split_line[0]
            shift   = split_line[1]
            student = split_line[2]

            if result.get(day)==None:
                result[day] = dict()

            result[day][shift] = student

        return opt_val, result


    def get_result():
        """
        Return a string representation of result.
        """
        return self.result

    def write_result(outFile):
        """
        Write result in the given output file.

        Parameters:
        -----------
            - `outFile` is the file to create (or overwrite)
        """
        with open(outFile, 'w') as out:
            out.write(result)

def get_all_shifts(calendar):
    """
    Return a sorted set containing all the shifts which may occur in a single day.
    """
    shift_names = set()
    for k, d in enumerate(calendar.keys()):
         for k, t in enumerate(calendar.get(d).keys()):
             shift_names.add(t)
    return sorted(shift_names)

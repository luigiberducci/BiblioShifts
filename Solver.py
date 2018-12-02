# File:     Solver.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import sys
import subprocess
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

    def config_problem(self, participants, options, calendar, minMaxShifts):
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
        self.data_content += " * OPL 12.8.0.0 Data\n"
        self.data_content += " * Author: Luigi Berducci\n"
        self.data_content += " * Creation Date: {}\n".format(datetime.date.today())
        self.data_content += " * \n"
        self.data_content += " * Name: {}\n".format(self.problem)
        self.data_content += " *********************************************/\n"
        self.data_content += "\n"

        # Parameters
        self.data_content += "/* Define the parameters */\n"
        self.data_content += "numStudents = {};\n".format(len(participants))
        self.data_content += "numDays     = {};\n".format(len(options.keys()))
        self.data_content += "numShifts   = {};\n".format(len(all_shifts))
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

        # Existance of shifts
        num_existing_shifts = 0
        self.data_content += "/* Define the existing shifts */\n"
        self.data_content += "Existance = #[\n"
        for k, d_name in enumerate(options.keys()):
            string_array = []
            for kk, s_name in enumerate(all_shifts):
                if s_name in options.get(d_name):
                    string_array.append(1)
                    num_existing_shifts = num_existing_shifts + 1
                else:
                    string_array.append(0)
            if k == len(options.keys())-1:
                self.data_content += "    {}: {}\n".format(k+1, str(string_array))
            else:
                self.data_content += "    {}: {},\n".format(k+1, str(string_array))
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
        for k, p_id in enumerate(minMaxShifts):
            if minMaxShifts.get(p_id)[0] == None:
                minMaxShifts[p_id] = (num_remaining_shifts//len(participants),
                                      minMaxShifts.get(p_id)[1])
            if k == len(minMaxShifts)-1:
                self.data_content += "    {}: {}\n".format(k+1, minMaxShifts.get(p_id)[0])
            else:
                self.data_content += "    {}: {},\n".format(k+1, minMaxShifts.get(p_id)[0])
        self.data_content += "]#;\n"
        self.data_content += "\n"

        # Maximum number of shifts for each students
        self.data_content += "/* Define the max number of shifts to assign to students */\n"
        self.data_content += "MaxNumShifts = #[\n"
        for k, p_id in enumerate(minMaxShifts):
            if minMaxShifts.get(p_id)[1] == None:
                minMaxShifts[p_id] = (minMaxShifts.get(p_id)[0], num_existing_shifts)
            if k == len(minMaxShifts)-1:
                self.data_content += "    {}: {}\n".format(k+1, minMaxShifts.get(p_id)[1])
            else:
                self.data_content += "    {}: {},\n".format(k+1, minMaxShifts.get(p_id)[1])
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
        print("Here")
        if self.opl_exe == "" or self.model_file == "" or self.data_file == "":
            return
        print("Here")
        subprocess.call([self.opl_exe, self.model_file, self.data_file])


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

# Turni biblioteca

The following software is used to assign shifts to people that work in the CS dept. library of the University of Rome "La Sapienza".

It performs automatic rostering by first parsing data from a Doodle poll, then solve a Integer Linear Programming Problem to assign a poll participant to each option of the poll, according to expressed availabilities.

## Requirements

The following libraries must be installed:

- [Python 3.6](https://www.python.org/) This software is written in Python
- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) The ILP problem is solved using CPLEX
- [OPL](https://www.ibm.com/analytics/optimization-modeling) The problem is formulated using OPL
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) This Python package is used to write the output result

All the listed softwares need to be properly configured according to the machine on which are executed.
Notice that the CPLEX executable path has to be written in the config file because it will be invoked to solve the problem.
i
## Usage
I tried to parametrize the program execution creating a configuration file `config.in`. It allows to define the input/output files, give a name to the problem and set the most appropriate model. Changing this file, you could also extend the software defining new models.

To run the software, open the terminal, move to this directory and write:
python3 main.py <poll-ID> [offline]

Once you pulled the Doodle poll and defined the model, the software creates a data file and then you never need to pull data from Doodle. Then, writing "offline" as third input parameter, the software skip this initial phase and run the solver starting from the data file currently defined.

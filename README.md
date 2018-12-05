# BiblioShifts

The following software is used to assign shifts to people that work in the CS Dept. library of the University of Rome "La Sapienza".

It represents an extension of the `turni-biblioteca` software by Cristian Di Pierantonio, who modeled this problem as a CSP.

This version performs automatic rostering by first parsing data from a Doodle poll, then solve a Integer Linear Programming Problem to assign a poll participant to each option of the poll, according to expressed availabilities. Finally, it produces a `xlsx` output file which contains an Excel representation of the computed assignment.

**Enjoy!**

## Updates
**UPDATE 04.12.2018**: Changed the model introducing and objective function which improves assignment balancing. It is defined as minimization of mean variance, formally: 

*`1/n sum_{s in students} (number_of_shifts_assigned_to[s] - avg_shifts_assigned)^2`*

where 

*   *`number_of_shifts_assigned_to[s]` is the number of shifts assigned to the student `s`*
*   *`avg_shifts_assigned` is computed as `total_number_of_shifts`/`number_of_students`*

Notice that this update make the current model NOT LINEAR but since CPLEX supports quadratic objective function, this is still efficiently solved.

**UPDATE 05.12.2018**: New model for minimize the number of overall trips required to cover all the shifts. Often, some students prefer to do more than one shift per day. If this is allowed by the library manager, then this model minimize the number of trips that the students have to do to reach the university. The main difference with the previous model is the objective function which minimize the number of day that each student spends in the library, formally:

*`sum_{s in students, d in days} Trips[s][d]`*

where

*    *`Trips[s][d]` is 1 if the student `s` has at least one shift in the day `d`, 0 otherwise*

Notice that this model is LINEAR but doesn't implement a balanced assignment because CPLEX allows only one objective function. Then you have to play with min-max number of shifts per student to manually implement balancing.

## Requirements

The following libraries must be installed:

- [Python 3.6](https://www.python.org/) This software is written in Python
- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) The ILP problem is solved using CPLEX
- [OPL](https://www.ibm.com/analytics/optimization-modeling) The problem is formulated using OPL
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) This Python package is used to write the output result

All the above softwares need to be properly configured according to the machine on which are executed.
Furthermore, the CPLEX executable path has to be written in the config file `config.in` because it will be invoked to solve the problem by the software.

## Usage
I tried to parametrize the program execution creating a configuration file `config.in`. It allows to define the input/output files, give a name to the problem and set the most appropriate model. Changing this file, you could also extend the software defining new models.

To run the software, open the terminal, move to this directory and write:
`python3 main.py <poll-ID> [offline]`

Once you pulled the Doodle poll and defined the model, the software creates a data file and then you never need to pull data from Doodle. Then, writing "offline" as third input parameter, the software skip this initial phase and run the solver starting from the data file currently defined.

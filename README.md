# Turni biblioteca

The following software is used to assign shifts to people that work in the CS dept. library of the University of Rome "La Sapienza".

It performs automatic rostering by first parsing data from a Doodle poll, then solve a Integer Linear Programming Problem to assign a poll participant to each option of the poll, according to expressed availabilities.

## Requirements

The following libraries must be installed:

- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer) The ILP problem is solver using CPLEX
- [OPL](https://www.ibm.com/analytics/optimization-modeling) The problem is formulated using OPL
- [Python 3.6](https://www.python.org/) This software is composed by few Python classes

All the listed softwares need to be properly configured according to the machine on which are executed.
Notice that the CPLEX executable path has to be written in the config file because it will be invoked to solve the problem.

## Usage
Still to be defined. Working on it.

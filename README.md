# Turni biblioteca

The following software is used to assign shifts to people that work in the CS dept. library of La Sapienza.

It performs automatic rostering by first parsing data from a Doodle poll, then solve a Integer Linear Programming to assign a poll participant to each option of the poll, according to expressed availabilities.

## Requirements

The following libraries must be installed:

- [CPLEX](https://www.ibm.com/analytics/cplex-optimizer)

## Usage

`python shifts.py <poll-ID>`

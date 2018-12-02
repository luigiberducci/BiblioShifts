# File:     DoodleParser.py
#
# Author:   Luigi Berducci
# Date:     2018-11-30

import sys
import datetime
import requests
import json

class DoodleParser:
    """
    Retrieves poll data from doodle.com and fill data structure
    for participants, options and preferences.
    """
    pollID       = ""
    participants = []
    options      = dict()
    calendar     = dict()

    def __init__(self, pollID):
        """
        Build the DoodleParser object defining the pollID.

        Parameteres:
        ------------
            - `pollID`: poll identifier contained in the doodle URL address
        """
        JSON = requests.get("https://doodle.com/api/v2.0/polls/" + pollID).content.decode('utf-8')
        JSON = json.loads(JSON)

        # Fill participants dict
        for participant in JSON['participants']:
            pName = participant['name']
            self.participants.append(pName)

        # Extract all the options (shifts)
        flat_options = [ datetime.datetime.fromtimestamp(x['start']/1000)
                         for x in JSON['options']]

        # Initialize options dict creating an empty list for each day
        for d in flat_options:
            self.options[format_date(d)] = []

        # Fill the options dict
        for d in flat_options:
            self.options[format_date(d)].append(format_time(d))

        # Initialize calendar dict creating an empty list for each option (day, shift)
        for k, d in enumerate(self.options.keys()):
            self.calendar[d] = dict()
            for k, t in enumerate(self.options.get(d)):
                self.calendar[d][t] = list()

        # Fill list of participant who express preference for option (day, shift)
        for participant in JSON['participants']:
            pID   = participant['id']
            pName = participant['name']

            for k, pref in enumerate(participant['preferences']):
                if pref<=0:     # Check if preference is not given
                    continue
                (d, t) = self.map_opt_to_calendar(k)
                self.calendar[d][t].append(pName)

    def get_participants(self):
        """
        Return the participants dict which map id->name, where
            - `id` is an integer identifier
            - `name` is the participant name
        """
        return self.participants

    def get_options(self):
        """
        Return the options dict which map day->list, where
            - `day` is a date
            - `list` is the collection of shifts in `day`
        """
        return self.options

    def get_calendar(self):
        """
        Return the calendar of preferences which map day->pref, where
            - `day` is a date
            - `pref` is a dict which map shift->participants, where
                - `shift` is a shift in `day`
                - `participants` is a list of participants which express this preference
        """
        return self.calendar

    def map_opt_to_calendar(self, i):
        """
        Retrieves the (day, shift) associated to the i-th options
        in flatten options representation.

        Parameters:
        -----------
            - `i`: index of the options

        Returns:
        -------
        a tuple (day, shift) where
            - `day`   is the identifier of the day associated to the i-th options
            - `shift` is the identifier of the shift associated to the i-th options
        """
        kk = 0

        for k, d in enumerate(self.options.keys()):
            for k, t in enumerate(self.options.get(d)):
                if kk == i:
                    return (d, t)
                kk = kk + 1
        return (d, t)

def format_date(d):
    """ Format a datetime as yyyy-mm-dd """
    return str(d.year) + "-" + str(d.month).zfill(2) + "-" + str(d.day).zfill(2)

def format_time(d):
    """ Format a datetime as hh:mm """
    return str(d.hour).zfill(2) + ":" + str(d.minute).zfill(2)

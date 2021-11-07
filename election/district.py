# -*- coding: utf-8 -*-

"""

"""
import copy
import logging
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


class Party:
    parameters = {
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    @classmethod
    def set_parameters(cls, new_parameters: dict):
        """

        :param new_parameters:
        """
        cls.parameters = {**cls.parameters, **new_parameters}

    def __init__(self, name: str, votes: int, short_name: str = None, method: str = "modified"):
        """
        A political party
        :param name: name of political party
        :param votes: nr of votes
        :param short_name: Abbreviation of party name
        :param method: normal or modified St Lagües
        """

        self.name = name
        self.district = None
        self.short_name = short_name
        self._votes = votes
        self.method = method
        self._representatives = 0

    def __repr__(self):
        return self.name

    def __add__(self, other):
        """
        Used to add votes and representatives from the same Party in different districts
        """
        if self.name != other.name:
            msg = (
                f"Party names differ: '{self.name}' and '{other.name}'. "
                f"Resulting party is named '{self.name}'"
            )
            logger.warning(msg)
        p = copy.deepcopy(self)
        p._votes = self._votes + other._votes
        p.representatives = self.representatives + other.representatives
        return p

    @property
    def representatives(self):
        return self._representatives

    @property
    def coefficient(self):
        return self._votes

    @representatives.setter
    def representatives(self, a):
        self._representatives = a

    @property
    def quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            quotient = self.coefficient / self.parameters["st_lagues_factor"]
        else:

            quotient = self.coefficient / (
                self.parameters["divide_factor"] * self.representatives + 1
            )
        return quotient

    def calc_quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            coeff = self.coefficient / self.parameters["st_lagues_factor"]
        else:

            coeff = self.coefficient / (self.parameters["divide_factor"] * self.representatives + 1)
        return coeff


class District(Party):
    parameters = {
        "area_importance": 1.8,  # Used in Norway
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    def __init__(self, area: float, population: int, name: str, method: str = "normal"):
        """

        :param area: area of district in km2
        :param population: nr of inhabitants in district
        :param name: name of district
        :param method: method to calculate division number

        """
        if (area < 0) or (population < 0):
            raise ValueError("Area and population must be positive")

        self._area = area
        self._population = int(population)
        self.name = name
        self._representatives = 0
        self.method = method
        self.parties: Optional[List[Party]] = None

    @property
    def votes_per_representative(self) -> int:
        """
        District factor, number of valid votes per representative. Used when distributing
        leveling seats
        """
        return int(self.district_votes / self.representatives)

    @property
    def coefficient(self):
        return self._area * self.parameters["area_importance"] + self._population

    @property
    def district_votes(self) -> int:
        """
        Gives total number of votes in the district
        """
        return sum([p._votes for p in self.parties])

    def append_parties(self, parties: List[Party]):
        """
        Adds parties to a county
        """
        if self.parties is None:
            self.parties = []
        for party in parties:
            party.district = self.name
        self.parties.extend(parties)

    def add_leveling_seat(self):
        """
        Adds leveling seat to the county
        """
        self.representatives += 1

    def calc_ordinary_representatives(self):
        """
        Calculates each party's representatives in the district, excluding leveling seat.
        """

        for _ in range(self.representatives - 1):
            self.parties.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_party = self.parties[0]
            acquiring_party.representatives += 1

    def parties_with_reps(self):
        """
        gives name of parties with representatives
        :return: list of parties (strings)
        """

        return [p.name for p in self.parties if p.representatives > 0]

    def get_representatives_per_party(self) -> pd.DataFrame:
        data = [
            {"party": p.name, "representatives": p.representatives, "district": p.district}
            for p in self.parties
        ]
        df = pd.DataFrame(data)
        return df.set_index("party")

# -*- coding: utf-8 -*-

"""

"""
import copy
from typing import List, Optional

import pandas as pd

from election.party import Party


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

    def __add__(self, other):
        """
        Used to add votes and representatives from the same Party in different districts
        """
        p = copy.deepcopy(self)
        p._area = self._area + other._area
        p._population = self._population + other._population
        return p

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
            {"party": p.short_name, "representatives": p.representatives, "district": p.district}
            for p in self.parties
        ]
        df = pd.DataFrame(data)
        return df.set_index("party")

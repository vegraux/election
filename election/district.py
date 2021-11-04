# -*- coding: utf-8 -*-

"""

"""
import copy
from typing import List

import pandas as pd


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

    def __init__(
        self, name: str, votes: int, district: str, short_name: str = None, method: str = "modified"
    ):
        """
        A political party
        :param name: name of political party
        :param votes: nr of votes
        :param short_name: Abbreviation of party name
        :param method: normal or modified St Lagües
        """

        self.name = name
        self.district = district
        self.short_name = short_name
        self._votes = votes
        self._method = method
        self._representatives = 0
        self._coefficient = copy.copy(votes)
        self.quotient = self.calc_quotient()

    @property
    def representatives(self):
        return self._representatives

    @representatives.setter
    def representatives(self, a):
        self._representatives = a
        self.quotient = self.calc_quotient()

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method: str):
        self._method = method
        self.quotient = self.calc_quotient()

    def calc_quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            coeff = self._coefficient / self.parameters["st_lagues_factor"]
        else:

            coeff = self._coefficient / (
                self.parameters["divide_factor"] * self.representatives + 1
            )
        return coeff


class District(Party):
    parameters = {
        "area_importance": 1.8,  # Used in Norway
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    def __init__(
        self,
        area: float,
        population: int,
        name: str,
        method: str = "normal",
        parties: List[Party] = None,
    ):
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
        self._method = method
        self._coefficient = self.calc_coefficient()
        self.quotient = self.calc_quotient()
        self.parties = parties

    def calc_coefficient(self):
        return self._area * self.parameters["area_importance"] + self._population

    def add_parties(self, parties):
        """

        :param parties: list of Party objects
        :type parties: List
        """
        if self.parties is None:
            self.parties = []

        for party in parties:
            self.parties.append(party)

    def count_district_votes(self):
        return sum([p._votes for p in self.parties])

    def add_leveling_seat(self):
        """
        Adds leveling seat to the county
        """
        self.representatives += 1

    def calc_representatives(self):
        """
        Calculates each party's representatives in the district
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

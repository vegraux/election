# -*- coding: utf-8 -*-

"""

"""
import copy

__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"


class County:
    parameters = {
        "area_importance": 1.8,  # Used in Norway
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    @classmethod
    def set_parameters(cls, new_parameters):
        """

        :param new_parameters:
        :type new_parameters: dict
        """
        cls.parameters = {**cls.parameters, **new_parameters}

    def __init__(self, area=0, population=0, name="NoName"):
        """

        :param area: area of county in km2
        :type   area: float
        :param population: nr of inhabitants in county
        :type population:  int
        :param name: name of county
        :type name: str

        """
        if (area < 0) or (population < 0):
            raise ValueError("Area and population must be positive")

        self._area = area
        self._population = int(population)
        self._name = name
        self.representatives = 0
        self._distribution = self.calc_distribution()
        self.divide_nr = self.calc_distribution()
        self.parties = None

    def calc_distribution(self):
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

    def count_county_votes(self):
        return sum([p._votes for p in self.parties])

    def calc_div_nr(self, method="normal"):

        if method == "normal":
            return self._distribution / (
                self.parameters["divide_factor"] * self.representatives + 1
            )

        if method == "modified":
            if self.representatives == 0:
                return self._distribution / self.parameters["st_lagues_factor"]

            else:
                return self._distribution / (
                    self.parameters["divide_factor"] * self.representatives + 1
                )

    def calc_representatives(self, method="modified"):
        """
        Calculates each party's representatives in that county
        """

        if method == "modified":
            for party in self.parties:
                party.divide_nr = party.calc_div_nr(method=method)

        for _ in range(self.representatives - 1):
            self.parties.sort(key=lambda x: x.divide_nr, reverse=True)
            self.parties[0].representatives += 1
            self.parties[0].divide_nr = self.parties[0].calc_div_nr(method=method)

    def parties_with_reps(self):
        """
        gives name of parties with representatives
        :return: list of parties (strings)
        """

        return [p._name for p in self.parties if p.representatives > 0]


class Party:
    parameters = {
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    @classmethod
    def set_parameters(cls, new_parameters):
        """

        :param new_parameters:
        :type new_parameters: dict
        """
        cls.parameters = {**cls.parameters, **new_parameters}

    def __init__(self, name, votes):
        """
        A political party
        :param name: name of political party
        :type name: str
        :param votes: nr of votes
        :type votes: int
        """

        self._name = name
        self._votes = votes
        self.divide_nr = copy.copy(votes)
        self.representatives = 0

    def calc_div_nr(self, method="normal"):

        if method == "normal":
            return self._votes / (
                self.parameters["divide_factor"] * self.representatives + 1
            )

        if method == "modified":
            if self.representatives == 0:
                return self._votes / self.parameters["st_lagues_factor"]

            else:
                return self._votes / (
                    self.parameters["divide_factor"] * self.representatives + 1
                )

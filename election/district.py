# -*- coding: utf-8 -*-

"""

"""
import copy


class District:
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

    def __init__(self, area: float, population: int, name: str, method: str = "normal"):
        """

        :param area: area of county in km2
        :param population: nr of inhabitants in county
        :param name: name of county
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
        self.parties = None

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

    def count_county_votes(self):
        return sum([p._votes for p in self.parties])

    def calc_quotient(self):
        if (self.method == "modified") and (self.representatives == 0):
            coeff = self._coefficient / self.parameters["st_lagues_factor"]
        else:

            coeff = self._coefficient / (
                self.parameters["divide_factor"] * self.representatives + 1
            )
        return coeff

    def add_leveling_seat(self):
        self.representatives += 1

    def calc_representatives(self, method="modified"):
        """
        Calculates each party's representatives in that county
        """

        if method == "modified":
            for party in self.parties:
                party.quotient = party.calc_quotient(method=method)

        for _ in range(self.representatives - 1):
            self.parties.sort(key=lambda x: x.quotient, reverse=True)
            self.parties[0].representatives += 1
            self.parties[0].quotient = self.parties[0].calc_quotient(method=method)

    def parties_with_reps(self):
        """
        gives name of parties with representatives
        :return: list of parties (strings)
        """

        return [p.name for p in self.parties if p.representatives > 0]


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
            return self._votes / (self.parameters["divide_factor"] * self.representatives + 1)

        if method == "modified":
            if self.representatives == 0:
                return self._votes / self.parameters["st_lagues_factor"]

            else:
                return self._votes / (self.parameters["divide_factor"] * self.representatives + 1)

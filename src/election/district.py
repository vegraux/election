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

    def __init__(self, area: float, population: int, name: str, method: str = "modified"):
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
        Used to add area and population from different districts
        """
        district = copy.deepcopy(self)
        district._area = self._area + other._area
        district._population = self._population + other._population
        return district

    def __len__(self) -> int:
        """
        Defined to be number of parties in the district
        """
        return len(self.parties)

    @property
    def percent_of_votes_per_party(self) -> pd.DataFrame:
        return self.votes_per_party / self.district_votes * 100


    @property
    def votes_per_party(self) -> pd.DataFrame:
        data = []
        if not self.parties:
            return pd.DataFrame()

        for party in self.parties:
            data.append({"name": party.short_name, "percent": party._votes})
        return pd.DataFrame(data).sort_values(by="percent", ascending=False).set_index("name")


    @property
    def votes_per_representative(self) -> float:
        """
        District factor, number of votes per representative. Used when distributing
        leveling seats. 1 is subtracted to the leveling seat in the district
        """
        return self.district_votes / (self.representatives - 1)

    @property
    def coefficient(self) -> float:
        """
        Coefficient (dividend) used to distribute district representatives
        """
        return self._area * self.parameters["area_importance"] + self._population

    @property
    def rep_per_party(self) -> pd.Series:
        """
        Convenience that gives pd.Series instead of pd.DataFrame as
        self.get_representatives_per_party() does
        """
        if not self.parties:
            return pd.Series([0], name="representatives")
        return self.get_representatives_per_party()["representatives"]

    @property
    def district_votes(self) -> int:
        """
        Gives total number of votes in the district
        """
        return sum([p._votes for p in self.parties])

    @property
    def distributed_representatives(self) -> int:
        """
        Gives total number of distributed representatives in the district. Can differ from
        self.representatives (feature not bug, imo)
        """
        return sum([p.representatives for p in self.parties])

    def reset_party_representatives(self):
        """
        Sets distributed representatives to 0 for all parties
        """
        for party in self.parties:
            party.reset_representatives()

    def append_parties(self, parties: List[Party]):
        """
        Adds parties to a county
        """
        if self.parties is None:
            self.parties = []
        for party in parties:
            party.district = self.name
        self.parties.extend(parties)

    def find_parties(self, party_names: List[str]) -> List[Party]:
        """
        Finds party instances for the given list of short names for parties
        """
        return [p for p in self.parties if p.short_name in party_names]

    def add_leveling_seat(self):
        """
        Adds leveling seat to the county
        """
        self.representatives += 1

    def calc_ordinary_representatives(self):
        """
        Calculates each party's representatives in the district, excluding leveling seat.
        """
        self.distribute_party_representatives(self.parties, self.representatives - 1)

    @staticmethod
    def distribute_party_representatives(parties: List[Party], num_rep: int):
        """
        Iterates over a list of Party and distributes num_rep representatives.
        """

        for _ in range(num_rep):
            parties.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_party = parties[0]
            if acquiring_party.short_name == "BLANKE":
                acquiring_party = parties[1]
            acquiring_party.representatives += 1

    def get_representatives_per_party(self) -> pd.DataFrame:
        """
        Gives DataFrame with data for short name, number of representatives
        and district for all parties
        """
        data = [
            {"party": p.short_name, "representatives": p.representatives, "district": p.district}
            for p in self.parties
        ]
        df = pd.DataFrame(data)
        return df.set_index("party")


class NationDistrict(District):
    def __init__(self, districts: List[District]):
        super().__init__(area=1, population=1, name="Nation")
        self.parties = self.set_national_district(districts)

    def set_national_district(self, districts: List[District]) -> List[Party]:
        """
        Loops over all districts and sums the votes for each party
        """
        national_parties = {}
        districts = copy.deepcopy(districts)
        for district in districts:
            for party in district.parties:
                if party.name not in national_parties:
                    national_parties[party.name] = party
                else:
                    national_parties[party.name] += party
        return list(national_parties.values())

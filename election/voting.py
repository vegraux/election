# -*- coding: utf-8 -*-

"""

"""
import copy
from typing import List

import numpy as np
import pandas as pd

from election.district import District, Party


class Nation:
    def __init__(
        self, districts: List[District] = None, cutoff: float = 4, method: str = "modified"
    ):
        self.cutoff = cutoff
        self.districts = districts if districts is not None else []
        self.method = method
        self.district_representatives = None
        self.party_representatives = None

    def calc_district_representatives(self, tot_rep: int = 150):
        """
        Distribute total national representatives to the districts
        :param tot_rep: Total number of ordinary representatives
        :return:
        """
        for district in self.districts:
            district.add_leveling_seat()

        for _ in range(tot_rep):
            self.districts.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_district = self.districts[0]
            acquiring_district.representatives += 1
        self.district_representatives = self.get_district_representatives()

    def calc_party_representatives(self):
        for district in self.districts:
            district.calc_ordinary_representatives()
        self.party_representatives = self.get_party_representative()

    def calc_ordinary_representatives(self, tot_rep: int = 150):
        self.calc_district_representatives(tot_rep=tot_rep)
        self.calc_party_representatives()

    def represented_parties(self):
        reps_parties = []
        for district in self.districts:
            district_parties = district.parties_with_reps()
            for p in district_parties:
                if p not in reps_parties:
                    reps_parties.append(p)

        return reps_parties

    def get_district_quotient(self) -> pd.DataFrame:
        data = [
            {"name": district.name, "quotient": district.quotient} for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def get_district_representatives(self) -> pd.DataFrame:
        self.districts.sort(key=lambda x: x.name)
        data = [
            {"name": district.name, "representatives": district.representatives}
            for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def get_party_representative(self) -> pd.DataFrame:
        data_results = []
        for district in self.districts:
            data_results.append(district.get_representatives_per_party())
        df = pd.concat(data_results, axis=0)
        df = df.pivot(columns="district").replace({np.nan: 0})
        df.columns = df.columns.droplevel(0)
        df = df[df.sum(axis=1) > 0]
        df = df.astype(int).transpose()
        df = df.reindex(sorted(df.columns), axis=1)
        df = df.reindex(sorted(df.index), axis=0)
        return df

    def calc_leveling_seat(self):
        national_parties = self.calc_total_party_votes()
        _ = District(name="Nation", area=1, population=1, parties=national_parties)
        pass

    def calc_total_party_votes(self) -> List[Party]:
        """
        Loops over all districts and sums the votes for each party
        """
        national_parties = {}
        for district in self.districts:
            for party in district.parties:
                if party.name not in national_parties:
                    national_party = copy.deepcopy(party)
                    national_party.district = "Nation"
                    national_parties[party.name] = national_party
                else:
                    national_parties[party.name]._votes += party._votes
        return list(national_parties.values())

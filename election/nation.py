# -*- coding: utf-8 -*-

"""

"""
import copy
from typing import List, Optional

import numpy as np
import pandas as pd

from election.district import District


class Nation:
    def __init__(
        self, districts: List[District] = None, cutoff: float = 0.04, method: str = "modified"
    ):
        self.cutoff = cutoff
        self.districts = districts if districts is not None else []
        self.method = method
        self.district_representatives = None
        self.party_representatives = None
        self.national_district: Optional[District] = None
        self.leveling_seat_parties: Optional[District] = None

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

    def set_parties_over_cutoff(self):
        """
        Creates a District instance with parties over the defined cutoff.
        """
        district = copy.deepcopy(self.national_district)
        cutoff_parties = []
        for party in district.parties:
            if party.vote_percentage(district.district_votes) < self.cutoff:
                cutoff_parties.append(party)
                continue
            party.reset_representatives()
        for party in cutoff_parties:
            district.parties.remove(party)

        self.leveling_seat_parties = district

    def calc_leveling_seat_per_party(self):
        over_represented_party = True
        while over_represented_party:
            pass

    def set_national_district(self):
        """
        Loops over all districts and sums the votes for each party
        """
        national_district = District(name="Nation", area=1, population=1)
        national_parties = {}
        districts = copy.deepcopy(self.districts)
        for district in districts:
            for party in district.parties:
                if party.name not in national_parties:
                    party.district = "Nation"
                    national_parties[party.name] = party
                else:
                    national_parties[party.name] += party
        national_district.append_parties(list(national_parties.values()))
        self.national_district = national_district

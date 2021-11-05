# -*- coding: utf-8 -*-

"""

"""

from typing import List

import numpy as np
import pandas as pd

from election.district import District


class Nation:
    def __init__(
        self, districts: List[District] = None, cutoff: float = 4, method: str = "modified"
    ):
        self.cutoff = cutoff
        self.districts = districts if districts is not None else []
        self.method = method

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

    def calc_party_representatives(self):
        for district in self.districts:
            district.calc_representatives()

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
        df = df.astype(int)
        return df

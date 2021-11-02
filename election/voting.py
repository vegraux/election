# -*- coding: utf-8 -*-

"""

"""


from typing import List

import pandas as pd

from election.district import District


class Nation:
    def __init__(
        self, districts: List[District] = None, cutoff: float = 4, method: str = "modified"
    ):
        self.cutoff = cutoff
        self.districts = districts if districts is not None else []
        self.method = method

    def calc_representatives(self, tot_rep=150):
        for district in self.districts:
            district.add_leveling_seat()

        for _ in range(tot_rep):
            self.districts.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_district = self.districts[0]
            acquiring_district.representatives += 1

    def calc_rep_distribution(self, method="modified"):
        """
        Calculates and fits the district representatives to the parties
        for all the counties. calc_representatives must first have been run
        :return:
        """

        for district in self.districts:
            district.calc_representatives(method=method)

    def represented_parties(self):
        reps_parties = []
        for district in self.districts:
            district_parties = district.parties_with_reps()
            for p in district_parties:
                if p not in reps_parties:
                    reps_parties.append(p)

        return reps_parties

    def district_quotient(self):
        data = [
            {"name": district.name, "quotient": district.quotient} for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def district_representatives(self):
        self.districts.sort(key=lambda x: x.name)
        data = [
            {"name": district.name, "representatives": district.representatives}
            for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def national_mandates_count(self):
        """
        Creates a dataframe with the results of the election
        :return:
        """
        rep_parties = self.represented_parties()
        df_list = []
        index = []
        for district in self.districts:
            index.append(district.name)
            for party in district.parties:
                if party.name in rep_parties:
                    df_list.append(
                        {
                            "Party": party.name,
                            "District": district.name,
                            "Representatives": party.representatives,
                        }
                    )

        df = pd.DataFrame(df_list)
        df = df.pivot(index="District", columns="Party", values="Representatives")
        return df

    def make_dataframe(self):
        """
        makes dataframe for each party's mandates in every district
        :return:
        """
        pass

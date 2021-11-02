# -*- coding: utf-8 -*-

"""

"""

__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"

from typing import List

import pandas as pd

from election.district import District


class Nation:
    def __init__(
        self, counties: List[District] = None, cutoff: float = 4, method: str = "modified"
    ):
        self.cutoff = cutoff
        self.counties = counties if counties is not None else []
        self.method = method

    def calc_representatives(self, tot_rep=150):
        for county in self.counties:
            county.add_leveling_seat()

        for _ in range(tot_rep):
            self.counties.sort(key=lambda x: x.quotient, reverse=True)
            aquiring_county = self.counties[0]
            aquiring_county.representatives += 1

    def calc_rep_distribution(self, method="modified"):
        """
        Calculates and fits the district representatives to the parties
        for all the counties. calc_representatives must first have been run
        :return:
        """

        for county in self.counties:
            county.calc_representatives(method=method)

    def represented_parties(self):
        reps_parties = []
        for county in self.counties:
            county_parties = county.parties_with_reps()
            for p in county_parties:
                if p not in reps_parties:
                    reps_parties.append(p)

        return reps_parties

    def district_quotient(self):
        data = [{"name": county.name, "quotient": county.quotient} for county in self.counties]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def district_representatives(self):
        self.counties.sort(key=lambda x: x.name)
        data = [
            {"name": county.name, "representatives": county.representatives}
            for county in self.counties
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
        for county in self.counties:
            index.append(county.name)
            for party in county.parties:
                if party.name in rep_parties:
                    df_list.append(
                        {
                            "Party": party.name,
                            "County": county.name,
                            "Representatives": party.representatives,
                        }
                    )

        df = pd.DataFrame(df_list)
        df = df.pivot(index="County", columns="Party", values="Representatives")
        return df

    def make_dataframe(self):
        """
        makes dataframe for each party's mandates in every county
        :return:
        """
        pass

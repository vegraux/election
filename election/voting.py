# -*- coding: utf-8 -*-

"""

"""

__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"
import pandas as pd


class Nation:
    def __init__(self, counties=None, cutoff=4):
        self.cutoff = cutoff
        if counties is None:
            self.counties = []

        else:
            self.counties = counties

    def calc_representatives(self, method="normal", tot_rep=169):

        if method == "modified":
            for county in self.counties:
                county.divide_nr = county.calc_div_nr(method="modified")

        for _ in range(tot_rep):
            self.counties.sort(key=lambda x: x.divide_nr, reverse=True)
            self.counties[0].representatives += 1
            self.counties[0].divide_nr = self.counties[0].calc_div_nr(method=method)

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

    def national_mandates_count(self):
        """
        Creates a dataframe with the results of the election
        :return:
        """
        rep_parties = self.represented_parties()
        df_list = []
        index = []
        for county in self.counties:
            index.append(county._name)
            for party in county.parties:
                if party._name in rep_parties:
                    df_list.append(
                        {
                            "Party": party._name,
                            "County": county._name,
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

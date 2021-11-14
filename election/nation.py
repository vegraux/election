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
        self,
        districts: List[District] = None,
        electoral_threshold: float = 0.04,
        method: str = "modified",
        tot_rep: int = 150,
    ):
        self.electoral_threshold = electoral_threshold
        self.tot_rep = tot_rep
        self.districts = districts if districts is not None else []
        self.method = method
        self.district_representatives: Optional[pd.DataFrame] = None
        self.ordinary_party_representatives: Optional[pd.DataFrame] = None
        self.national_district: Optional[District] = None
        self.over_threshold_district: Optional[District] = None
        self.under_threshold_district: Optional[District] = None
        self.leveling_seats_factors: Optional[pd.DataFrame] = None
        self.leveling_seat_per_party: Optional[pd.Series] = None

    def calc_district_representatives(self):
        """
        Distribute total national representatives to the districts.
        """
        for district in self.districts:
            district.add_leveling_seat()

        for _ in range(self.tot_rep):
            self.districts.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_district = self.districts[0]
            acquiring_district.representatives += 1
        self.district_representatives = self.get_district_representatives()

    def calc_party_representatives(self):
        """
        Distributes the district representatives to a party for all districts in Nation.
        Leveling seats are not included here
        """
        for district in self.districts:
            district.calc_ordinary_representatives()
        self.ordinary_party_representatives = self.party_representatives

    def calc_ordinary_representatives(self):
        """
        Distributes district representatives first, then party representatives.
        Leveling seats are not included here
        """
        self.calc_district_representatives()
        self.calc_party_representatives()

    def get_district_quotient(self) -> pd.DataFrame:
        """
        DataFrame with quotient for all districts
        """
        data = [
            {"name": district.name, "quotient": district.quotient} for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    def get_district_representatives(self) -> pd.DataFrame:
        """
        DataFrame with district representatives for all districts
        """
        self.districts.sort(key=lambda x: x.name)
        data = [
            {"name": district.name, "representatives": district.representatives}
            for district in self.districts
        ]
        df = pd.DataFrame(data)
        return df.set_index("name")

    @property
    def party_representatives(self) -> pd.DataFrame:
        """
        DataFrame with number of representatives for each county and party. Only
        parties with representatives are included
        """
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

    def set_threshold_parties(self):
        """
        Sets District instances for parties over and under the defined electoral threshold.
        """
        over_threshold_district = copy.deepcopy(self.national_district)
        under_threshold_parties = []
        for party in over_threshold_district.parties:
            if party.vote_share(over_threshold_district.district_votes) < self.electoral_threshold:
                under_threshold_parties.append(party)

        for party in under_threshold_parties:
            over_threshold_district.parties.remove(party)
        under_threshold_district = District(1, 1, name="Under threshold")
        under_threshold_district.append_parties(under_threshold_parties)
        self.over_threshold_district = over_threshold_district
        self.under_threshold_district = under_threshold_district

    def set_leveling_seat_per_party(self):
        """
        Calculates the number of leveling seats a party should have, and returns
        the data as a pd.Series. The corresponding districts are not calculated here
        """
        districts = copy.deepcopy(self.over_threshold_district)
        real_representatives = self.party_representatives.sum()
        districts.representatives = self.get_total_rep_for_leveling_seat_calc()
        while True:
            districts.reset_party_representatives()
            districts.distribute_party_representatives(districts.parties, districts.representatives)
            leveling_seat_per_party = (districts.rep_per_party - real_representatives).dropna()
            parties_to_remove = leveling_seat_per_party[leveling_seat_per_party < 0]
            if len(parties_to_remove) == 0:
                break
            for party in districts.find_parties(parties_to_remove):
                districts.parties.remove(party)
                districts.representatives -= real_representatives[party.short_name]
        leveling_seat_per_party.name = "seats"
        self.leveling_seat_per_party = leveling_seat_per_party.convert_dtypes(np.int64)

    def set_leveling_seats_factors(self):
        leveling_seat_data = []
        for district in self.districts:
            for party in district.parties:
                party.method = "normal"
                factor = party.level_seat_factor(district.votes_per_representative)
                data = {"party": party.short_name, "district": district.name, "factor": factor}
                leveling_seat_data.append(data)
        df = pd.DataFrame(leveling_seat_data)
        self.leveling_seats_factors = df.sort_values(by="factor", ascending=False)

    def distribute_leveling_seats_to_parties(self):
        leveling_seat_per_party = pd.DataFrame(self.leveling_seat_per_party)
        leveling_seat_per_party["acquired"] = 0
        qualifying = self.leveling_seats_factors["party"].isin(leveling_seat_per_party.index)
        factors = self.leveling_seats_factors[qualifying]
        leveling_seat_data = []
        for _ in range(len(self.districts)):
            factors = factors.sort_values(by="factor", ascending=False)
            acquiring_party = factors.iloc[0, :].to_dict()
            acquiring_party["leveling seat"] = 1
            leveling_seat_per_party.loc[acquiring_party["party"], "acquired"] += 1
            leveling_seat_data.append(acquiring_party)
            factors = self.filter_leveling_seat_table(
                factors, leveling_seat_per_party, acquiring_party
            )
        df = pd.DataFrame(leveling_seat_data)
        df = df.pivot_table(
            index="district", columns="party", values="leveling seat", aggfunc="count"
        )
        df = df.replace({np.nan: 0}).astype(int)
        return df

    def filter_leveling_seat_table(
        self, factors: pd.DataFrame, leveling_seat_per_party: pd.DataFrame, acquiring_party: dict
    ) -> pd.DataFrame:
        """
        Filters out parties/districts that have received all its leveling seats
        """
        factors = factors[factors["district"] != acquiring_party["district"]]
        rest = leveling_seat_per_party["seats"] - leveling_seat_per_party["acquired"]
        return factors[factors["party"].isin(rest[rest > 0].index)]

    def get_total_rep_for_leveling_seat_calc(self) -> int:
        """
        Representatives from parties that don't qualify for a leveling seat due to a vote share
        under the electoral threshold, should be removed before distributing the representatives
        when the nation as a whole is regarded as a district
        """
        tot_rep = self.tot_rep + len(self.districts)
        remove_rep = self.under_threshold_district.rep_per_party.sum()
        return tot_rep - remove_rep

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
                    national_parties[party.name] = party
                else:
                    national_parties[party.name] += party
        national_district.append_parties(list(national_parties.values()))
        self.national_district = national_district

    def apply_leveling_seat_results(self, leveling_seat: pd.DataFrame):
        """
        Adds the leveling seats to the relevant Party instances as given by
        the DataFrame leveling_seat
        """
        for district in self.districts:
            acquiring_party_name = leveling_seat.loc[district.name, :].idxmax()
            acquiring_party = district.find_parties(acquiring_party_name)[0]
            acquiring_party.representatives += 1

    def simulate_election(self):
        self.calc_ordinary_representatives()
        self.set_national_district()
        self.set_threshold_parties()
        leveling_seats_factors = self.set_leveling_seats_factors()
        leveling_seat_per_party = self.set_leveling_seat_per_party()
        seats = self.distribute_leveling_seats_to_parties(
            leveling_seat_per_party, leveling_seats_factors
        )
        self.apply_leveling_seat_results(seats)

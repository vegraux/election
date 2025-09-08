import copy
from typing import ClassVar, Self

import pandas as pd

from election.party import OrdinaryRepresentative, Party, Representative

NON_PARTIES = ["BLANKE", "Andre", "Andre2"]


class District(Party):
    parameters: ClassVar = {
        "area_importance": 1.8,  # Used in Norway
        "divide_factor": 2,  # Laguës' method (divide_factor*rep + 1)
        "st_lagues_factor": 1.4,
    }

    def __init__(self, area: float, population: int, name: str, method: str = "modified") -> None:
        if (area < 0) or (population < 0):
            raise ValueError("Area and population must be positive")

        self.area = area
        self.population = int(population)
        self.name = name
        self._representatives = []
        self.party_representatives = []
        self.method = method
        self.parties: list[Party] | None = None

    def __add__(self, other: Self) -> Self:
        """Used to add area and population from different districts."""
        district = copy.deepcopy(self)
        district.area = self.area + other.area
        district.population = self.population + other.population
        return district

    def __len__(self) -> int:
        """Defined to be number of parties in the district."""
        return len(self.parties)

    @property
    def percent_of_votes_per_party(self) -> pd.DataFrame:
        return self.votes_per_party / self.district_votes * 100

    @property
    def votes_per_party(self) -> pd.DataFrame:
        if not self.parties:
            return pd.DataFrame()
        data = [{"name": party.short_name, "percent": party._votes} for party in self.parties]
        return pd.DataFrame(data).sort_values(by="percent", ascending=False).set_index("name")

    @property
    def votes_per_representative(self) -> float:
        """District factor, number of votes per representative.

        Used when distributing leveling seats. 1 is subtracted to the leveling seat in the district.
        """
        return self.district_votes / (self.nr_representatives - 1)

    def calc_needed_votes_to_last_rep(self) -> pd.DataFrame:
        """Calculate how many extra votes each party needs to win the last representative."""
        # quotient of the last winning party
        last_rep_quotient = self.party_representatives[-1].quotient

        # q1 < q2 -> q1 < v2/d2  -> q1*d2 < v2
        # votes needed
        data = [
            {
                "party": p.name,
                "district": self.name,
                "quotient": p.quotient,
                "votes_needed": last_rep_quotient * p.dividend(p.nr_representatives) - p._votes,
            }
            for p in self.parties
        ]
        return pd.DataFrame(data)

    @property
    def coefficient(self) -> float:
        """Coefficient (dividend) used to distribute district representatives."""
        return self.area * self.parameters["area_importance"] + self.population

    @property
    def rep_per_party(self) -> pd.Series:
        if not self.parties:
            return pd.Series([0], name="representatives")
        return self.get_representatives_per_party()["representatives"]

    @property
    def district_votes(self) -> int:
        """Gives total number of votes in the district."""
        return sum([p._votes for p in self.parties])

    @property
    def distributed_representatives(self) -> int:
        """Gives total number of distributed representatives in the district.

        Can differ from self.representatives (feature not bug, imo).
        """
        return sum([p.nr_representatives for p in self.parties])

    @property
    def quotient_per_party(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"district": self.name, "party": p.name, "quotient": p.quotient} for p in self.parties]
        ).sort_values(by="quotient")

    def reset_party_representatives(self) -> None:
        """Sets distributed representatives to 0 for all parties."""
        for party in self.parties:
            party.reset_representatives()

    def append_parties(self, parties: list[Party]) -> None:
        """Adds parties to a county."""
        if self.parties is None:
            self.parties = []
        for party in parties:
            party.district = self.name
        self.parties.extend(parties)

    def find_parties(self, party_names: list[str]) -> list[Party]:
        """Finds party instances for the given list of short names for parties."""
        return [p for p in self.parties if (p.short_name in party_names) or (p.name in party_names)]

    def add_leveling_seat(self) -> None:
        """Adds leveling seat to the county."""
        self._representatives.append(Representative(name=self.name))

    def calc_ordinary_representatives(self) -> None:
        """Calculates each party's representatives in the district, excluding leveling seat."""
        self.distribute_party_representatives(self.nr_representatives - 1)

    def distribute_party_representatives(self, num_rep: int) -> None:
        """Distributes num_rep representatives to the parties in the district."""
        for nr in range(1, num_rep + 1):
            self.parties.sort(key=lambda x: x.quotient, reverse=True)
            acquiring_party = self.parties[0]
            if acquiring_party.short_name in NON_PARTIES:
                acquiring_party = self.parties[1]
            rep = OrdinaryRepresentative(
                nr=nr,
                remaining_representative=num_rep - nr,
                quotient=acquiring_party.quotient,
                name=acquiring_party.name,
            )
            acquiring_party._representatives.append(rep)
            self.party_representatives.append(rep)

    def get_representatives_per_party(self) -> pd.DataFrame:
        """Gives DataFrame with data for short name, number of representatives and district for all parties."""
        data = [
            {"party": p.short_name, "representatives": p.nr_representatives, "district": p.district}
            for p in self.parties
        ]
        df = pd.DataFrame(data)
        return df.set_index("party")


class NationDistrict(District):
    def __init__(self, districts: list[District]) -> None:
        super().__init__(area=1, population=1, name="Nation")
        self.parties = self.set_national_district(districts)

    def set_national_district(self, districts: list[District]) -> list[Party]:
        """Loops over all districts and sums the votes for each party."""
        national_parties = {}
        districts = copy.deepcopy(districts)
        for district in districts:
            for party in district.parties:
                if party.name not in national_parties:
                    national_parties[party.name] = party
                else:
                    national_parties[party.name] += party
        return list(national_parties.values())

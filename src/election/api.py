import pathlib
from datetime import datetime
from enum import StrEnum

import httpx
import pandas as pd
import pydantic

from election.district import NON_PARTIES, District
from election.nation import Nation
from election.party import Party


class ElectionAPI(StrEnum):
    endpoint: str = "https://valgresultat.no/api"


class ElectionResponse(pydantic.BaseModel):
    pass


class ElectionType(StrEnum):
    storting = "ST"
    sameting = "SA"


class DistrictInfo(pydantic.BaseModel):
    navn: str
    nivaa: str
    nr: int
    valgaar: int
    valgtype: ElectionType


class VotesCount(pydantic.BaseModel):
    fhs: int
    total: int


class Votes(pydantic.BaseModel):
    antall: VotesCount


class VotesInfo(pydantic.BaseModel):
    resultat: Votes


class CountStats(pydantic.BaseModel):
    endelig: float
    forelopig: float
    forelopigFhs: float
    forelopigVts: float
    oppgjor: float


class Tidspunkt(pydantic.BaseModel):
    rapportGenerert: datetime
    sisteStemmer: datetime | None


class PartyInfo(pydantic.BaseModel):
    navn: str
    partikode: str
    partikategori: int


class PartyResult(pydantic.BaseModel):
    id: PartyInfo
    stemmer: VotesInfo

    @property
    def nr_votes(self) -> int:
        return self.stemmer.resultat.antall.total

    @property
    def name(self) -> str:
        return self.id.navn

    @property
    def short_name(self) -> str:
        return self.id.partikode


class DistrictResponse(pydantic.BaseModel):
    id: DistrictInfo
    opptalt: CountStats | None = None
    tidspunkt: Tidspunkt
    partier: list[PartyResult]

    @property
    def name(self) -> str:
        return self.id.navn


def get_nation_from_api(year: int) -> Nation:
    path = pathlib.Path(__file__).parent / "data"

    district_data = pd.read_csv(path / f"area_population_{year - 1}.csv", sep=";")

    districts = [
        District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2]) for _, row in district_data.iterrows()
    ]

    client = httpx.Client()
    nation = get_nation(client, year, districts)
    return nation


def get_nation(client: httpx.Client, year: int, districts: list[District]) -> Nation:
    year_data = client.get(f"{ElectionAPI.endpoint}/{year}/st")
    for link in year_data.json()["_links"]["related"]:
        # time.sleep(0.1)
        response = client.get(f"{ElectionAPI.endpoint}{link['href']}")
        district_data = DistrictResponse.model_validate(response.json())
        district = [d for d in districts if d.name == district_data.name].pop()
        print("data for: ", district.name)

        party_list = [
            Party(name=party.name, short_name=party.short_name, votes=party.nr_votes)
            for party in district_data.partier
            if party.short_name not in NON_PARTIES
        ]

        district.append_parties(party_list)

    return Nation(districts=districts)

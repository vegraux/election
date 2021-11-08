import pathlib

import numpy as np
import pandas as pd
import pytest
from testfixtures import LogCapture

from election.district import District
from election.nation import Nation
from election.party import Party


@pytest.fixture
def data_path():
    dir = pathlib.Path(__file__).parent.parent / "election/data"
    return dir


@pytest.fixture
def votes2021(data_path):
    dir = data_path / "votes_2021.csv"
    vote_data = pd.read_csv(dir, sep=";")
    return vote_data


@pytest.fixture
def district_data(data_path):
    dir = data_path / "area_population_2021.csv"
    district_data = pd.read_csv(dir, sep=";")
    return district_data


@pytest.fixture
def results2021_all_representatives(votes2021):
    df = votes2021.pivot_table(index="Partikode", columns="Fylkenavn", values="Antall mandater")
    df = df.replace({np.nan: 0})
    df = df[df.sum(axis=1) > 0]
    df = df.astype(int).transpose()
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reindex(sorted(df.index), axis=0)
    return df


@pytest.fixture
def results2021_ordinary_representatives(votes2021):
    votes2021["Ordinære mandater"] = (
        votes2021["Antall mandater"] - votes2021["Antall utjevningsmandater"]
    )
    df = votes2021.pivot_table(index="Partikode", columns="Fylkenavn", values="Ordinære mandater")
    df = df.replace({np.nan: 0})
    df = df[df.sum(axis=1) > 0]
    df = df.astype(int).transpose()
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reindex(sorted(df.index), axis=0)
    return df


@pytest.fixture
def results2021_leveling_representatives(votes2021):
    df = votes2021[votes2021["Antall utjevningsmandater"] > 0]
    df = df.pivot_table(index="Partikode", columns="Fylkenavn", values="Antall utjevningsmandater")
    df = df.replace({np.nan: 0})
    df = df[df.sum(axis=1) > 0]
    df = df.astype(int).transpose()
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reindex(sorted(df.index), axis=0)
    return df


@pytest.fixture
def nation2021(votes2021, district_data):
    districts = []
    for k, row in district_data.iterrows():
        district = row.iloc[0]
        district_vote_data = votes2021[votes2021["Fylkenavn"] == district]
        district_parties = []
        for _, party in district_vote_data.iterrows():
            p = Party(name=party.iloc[7], short_name=party.iloc[6], votes=party.iloc[12])
            district_parties.append(p)
        d = District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2])
        d.append_parties(district_parties)
        districts.append(d)
    norway = Nation(districts=districts)
    return norway


@pytest.fixture
def party_a():
    return Party(name="Party A", votes=100)


@pytest.fixture
def party_b():
    return Party(name="Party B", votes=200)


@pytest.fixture
def district1(party_a, party_b):
    district = District(area=1000, population=1000, name="foo2")
    district.append_parties(parties=[party_a, party_b])
    return district


@pytest.fixture
def district2(party_a, party_b):
    district = District(area=100, population=100, name="foo1")
    district.append_parties(parties=[party_a, party_b])
    return district


@pytest.fixture
def parties_with_representatives(district1):
    district1.representatives = 10
    district1.calc_ordinary_representatives()
    return district1.parties


@pytest.fixture
def nation(district1, district2):
    return Nation(districts=[district1, district2])


@pytest.fixture(autouse=True)
def capture():
    with LogCapture() as capture:
        yield capture

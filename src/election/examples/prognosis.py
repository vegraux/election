import copy
import pathlib
import re

import pandas as pd

from election.district import District
from election.nation import Nation
from election.party import Party

path = pathlib.Path(__file__).parent.parent / "data"
district_data = pd.read_csv(path / "area_population_2021.csv", sep=";")
vote_data = pd.read_csv(path / "votes_2021.csv", sep=";")

districts = []
for _k, row in district_data.iterrows():
    district = row.iloc[0]
    district_vote_data = vote_data[vote_data["Fylkenavn"] == district]
    district_parties = []
    for _, party in district_vote_data.iterrows():
        p = Party(name=party.iloc[7], short_name=party.iloc[6], votes=party.iloc[12])
        if p.short_name == "MDG":
            p._votes += 0
        district_parties.append(p)
    d = District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2])
    d.append_parties(district_parties)
    districts.append(d)

norway = Nation(districts=copy.deepcopy(districts))


poll_trondelag = pd.read_csv(path / "poll_sor_trondelag.csv", skiprows=[0, 1], sep=";")
poll_trondelag.iloc[:, 2:] = poll_trondelag.iloc[:, 2:].applymap(
    lambda x: float(re.findall(r"\d+,\d", x)[0].replace(",", "."))
)
trondelag = norway.districts[14]
fresh_poll = poll_trondelag.iloc[0, 2:]
name_map = {""}

names = ["FRP", "H", "SV", "RØDT", "SP", "MDG", "V", "A", "KRF"]
poll_names = ["Frp", "Høyre", "SV", "Rødt", "Sp", "MDG", "Venstre", "Ap", "KrF"]
name_map = dict(zip(names, poll_names, strict=False))

for party in trondelag.parties:
    if party.short_name in name_map:
        party._votes = fresh_poll.loc[name_map[party.short_name]]
    else:
        party._votes = 0


norway.simulate_election()

print(2)

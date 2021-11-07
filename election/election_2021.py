import copy

import pandas as pd

from election.district import District, Party
from election.voting import Nation

district_data = pd.read_csv("data/area_population_2021.csv", sep=";")
vote_data = pd.read_csv("data/votes_2021.csv", sep=";")
st_lagues = 1.4

districts = []
for k, row in district_data.iterrows():
    district = row.iloc[0]
    district_vote_data = vote_data[vote_data["Fylkenavn"] == district]
    district_parties = []
    for _, party in district_vote_data.iterrows():
        p = Party(name=party.iloc[7], short_name=party.iloc[6], votes=party.iloc[12])
        district_parties.append(p)
    d = District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2])
    d.append_parties(district_parties)
    districts.append(d)

District.set_parameters({"st_lagues_factor": st_lagues})
Party.set_parameters({"st_lagues_factor": st_lagues})

norway = Nation(districts=copy.deepcopy(districts))
norway.calc_ordinary_representatives()
norway.calc_leveling_seat()

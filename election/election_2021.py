import copy

import pandas as pd

from election.district import District, Party
from election.voting import Nation

district_data = pd.read_csv("data/area_population_2021.csv", sep=";")
vote_data = pd.read_csv("data/votes_2021.csv", sep=";")

st_lagues = 1.4

districts = []
for k, row in district_data.iterrows():
    districts.append(District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2]))
District.set_parameters({"st_lagues_factor": st_lagues})
Party.set_parameters({"st_lagues_factor": st_lagues})

norway = Nation(districts=copy.deepcopy(districts))
quotient = norway.district_quotient()
norway.calc_representatives()
representatives = norway.district_representatives()
pass

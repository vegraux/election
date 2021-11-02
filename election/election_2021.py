import copy

import pandas as pd

from election.district import District, Party
from election.voting import Nation

df = pd.read_csv("area_population.csv", sep=";")

st_lagues = 1.4

counties = []
for k, row in df.iterrows():
    counties.append(District(name=row.iloc[0], population=row.iloc[1], area=row.iloc[2]))
District.set_parameters({"st_lagues_factor": st_lagues})
Party.set_parameters({"st_lagues_factor": st_lagues})

norway = Nation(counties=copy.deepcopy(counties))
quotient = norway.district_quotient()
norway.calc_representatives()
representatives = norway.district_representatives()
pass

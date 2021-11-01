# -*- coding: utf-8 -*-

"""
Calculates the 150 district mandates
"""

import pandas as pd
from election.country import County, Party
from election.voting import Nation
import copy

#%%
__author__ = "Vegard Solberg"
# Read in the counties with area and population (1. jan 2012)
df = pd.read_excel("tabell.xlsx", skiprows=[0, 1, 2])
df = df.iloc[:, :4]

st_lagues = 4

counties = []
for k, row in df.iterrows():
    counties.append(County(name=row["Fylke"], population=row[2012], area=row["areal"]))
County.set_parameters({"st_lagues_factor": st_lagues})
Party.set_parameters({"st_lagues_factor": st_lagues})

norway = Nation(counties=copy.deepcopy(counties))
norway.calc_representatives(method="normal")

# Read in the votes in each county

votes_raw = pd.read_excel("tabell.xlsx", sheet_name="stemmer", index=1)
votes = votes_raw.iloc[
    :, 1:-1
]  # fylker er kolonner, parti er index, stemmer er verdier
votes.index = votes_raw.iloc[:, 0]
votes = votes.fillna(value=0, axis=0)

parties = votes.index

for county in norway.counties:
    county_votes = votes[county._name]
    county.add_parties(
        [
            Party(name=county_votes.index[k], votes=p_votes)
            for k, p_votes in enumerate(county_votes)
        ]
    )

norway.calc_rep_distribution(method="modified")

# print(norway.represented_parties())

print(norway.national_mandates_count().sum())

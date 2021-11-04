# -*- coding: utf-8 -*-

"""
Calculates the 150 district mandates
"""

import copy

import pandas as pd

from election.district import District, Party
from election.voting import Nation

__author__ = "Vegard Solberg"
# Read in the counties with area and population (1. jan 2012)
df = pd.read_excel("tabell.xlsx", skiprows=[0, 1, 2])
df = df.iloc[:, :4]

st_lagues = 4

counties = []
for k, row in df.iterrows():
    counties.append(District(name=row["Fylke"], population=row[2012], area=row["areal"]))
District.set_parameters({"st_lagues_factor": st_lagues})
Party.set_parameters({"st_lagues_factor": st_lagues})

norway = Nation(districts=copy.deepcopy(counties))
norway.calc_district_representatives()

# Read in the votes in each district

votes_raw = pd.read_excel("tabell.xlsx", sheet_name="stemmer", index=1)
votes = votes_raw.iloc[:, 1:-1]  # fylker er kolonner, parti er index, stemmer er verdier
votes.index = votes_raw.iloc[:, 0]
votes = votes.fillna(value=0, axis=0)

parties = votes.index

for district in norway.districts:
    district_votes = votes[district.name]
    district.add_parties(
        [
            Party(name=district_votes.index[k], votes=p_votes)
            for k, p_votes in enumerate(district_votes)
        ]
    )

norway.calc_rep_distribution(method="modified")

# print(norway.represented_parties())

print(norway.national_mandates_count().sum())

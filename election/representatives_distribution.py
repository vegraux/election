# -*- coding: utf-8 -*-

"""
Calculates the distribution of the 169 representatives in 2017
"""

import copy

import pandas as pd

from election.district import District
from election.voting import Nation

# %%
__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"

df = pd.read_excel("tabell.xlsx", skiprows=[0, 1, 2])
df = df.iloc[:, :4]

st_lagues = 1

counties = []
for k, row in df.iterrows():
    counties.append(District(name=row["Fylke"], population=row["befolkning"], area=row["areal"]))
District.set_parameters({"st_lagues_factor": st_lagues})

v1 = Nation(counties=copy.deepcopy(counties), method="modified")
v1.calc_representatives()

v2 = Nation(counties=copy.deepcopy(counties), method="normal")
v2.calc_representatives()

v1.counties.sort(key=lambda x: x.name)
v2.counties.sort(key=lambda x: x.name)

print("{0:^20} {1:^10} {2:^10} ".format("Fylke:", "normal:", "modified:"))
for i in range(len(v1.counties)):
    print(
        "{0:^20} {1:^10} {2:^10}".format(
            v2.counties[i].name, v1.counties[i].representatives, v2.counties[i].representatives
        )
    )

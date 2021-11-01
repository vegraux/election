# -*- coding: utf-8 -*-

"""
Calculates the distribution of the 169 representatives in 2017
"""

import pandas as pd
from country import County
from voting import Nation
import copy

# %%
__author__ = "Vegard Solberg"
__email__ = "vegard.ulriksen.solberg@nmbu.no"

df = pd.read_excel("tabell.xlsx", skiprows=[0, 1, 2])
df = df.iloc[:, :4]

st_lagues = 1

counties = []
for k, row in df.iterrows():
    counties.append(County(name=row[0], population=row[1], area=row[3]))
County.set_parameters({"st_lagues_factor": st_lagues})

v2 = Nation(counties=copy.deepcopy(counties))
v2.calc_representatives(method="modified")

v1 = Nation(counties=copy.deepcopy(counties))
v1.calc_representatives(method="normal")

v1.counties.sort(key=lambda x: x._name)
v2.counties.sort(key=lambda x: x._name)

print("{0:^20} {1:^10} {2:^10} ".format("Fylke:", "normal:", "modified:"))
for i in range(len(v1.counties)):
    print(
        "{0:^20} {1:^10} {2:^10}".format(
            v2.counties[i]._name,
            v1.counties[i].representatives,
            v2.counties[i].representatives,
        )
    )

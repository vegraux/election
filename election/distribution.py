# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 13:09:09 2018

@author: vegar
"""

import pandas as pd
import numpy as np
import copy


df = pd.read_excel("tabell.xlsx", skiprows=[0, 1, 2])

df = df[["Fylke", "befolkning", "areal", 2012]]
df[2012].astype("float")
fylker = df["Fylke"]

f0 = df["areal"] * 1.8 + df[2012]
fordelingstall = df["areal"] * 1.8 + df[2012]
mandater = np.zeros_like(fylker)
df["mandater"] = 169 * fordelingstall / fordelingstall.sum()
df["mandater"] = df["mandater"].round()
mand = np.array(np.zeros([19, 1]))
# gjør det med den metoden 1,3,5,7,etc

st_factor = 100  # første deletall
fordelingstall = fordelingstall / st_factor

for _ in range(169):
    i = fordelingstall.values.argmax()
    mand[i] += 1
    print(_, df["Fylke"][i], mand[i])
    kvotient = 1 + 2 * mand[i]
    fordelingstall[i] = f0[i] / kvotient

df["mandater_real"] = mand
# df['mandater_real'] += 1
print(df[["Fylke", "mandater_real"]])
#%%
# Regner ut de 150 distriktsmandatene
import copy


res_raw = pd.read_excel("tabell.xlsx", sheet_name="stemmer", index=1)
data = res_raw.iloc[:, 1:-1]  # fylker er kolonner, parti er index, stemmer er verdier
data.index = res_raw.iloc[:, 0]
data = data.fillna(value=0, axis=0)

partier = data.index

M = pd.DataFrame(
    np.zeros_like(data.values), columns=fylker
)  # her skal mandatene oppdateres


M.index = partier
deletall = [1.4, 3, 5, 7, 9, 11, 13, 15, 17, 19]  # deletall, modifisert metode

for k, fylke in enumerate(fylker):
    teller = 0
    stemmetall = copy.copy(data[fylke])
    stemmetall = stemmetall / deletall[0]

    # print('\n',fylke, '\n')
    for _ in range(int(df["mandater"][k]) - 1):
        i = stemmetall.values.argmax()
        # print(M.index[i])
        M[fylke][i] += 1
        n = int(M[fylke][i])
        stemmetall[i] = data[fylke][i] / (deletall[n])


# Mt = M.transpose().iloc[::-1]

#%%
# Fordeling av utgjevningsmandatene
partisum = data.sum(axis=1)
partisum = partisum.drop(index=["Blanke"])

prosent = 100 * partisum / partisum.sum()

upartier = [prosent.index[k] for k, parti in enumerate(prosent) if parti > 4]
upartier = np.array(upartier)


Mu = pd.DataFrame(index=upartier)
Mu["Umandater"] = np.zeros(upartier.shape)

deletall = np.arange(1, 200, 2)


overrep = True

while overrep:  # forsett så lenge det er overrepresentert partier
    upartisum = partisum[upartier]
    stemmetall = copy.copy(upartisum)
    stemmetall = stemmetall / 1.4

    rep_U = int(
        M.sum(axis=1)[upartier].sum()
    )  # antall mandater for parti over sperregrensa
    for _ in range(rep_U + 19):
        i = stemmetall.values.argmax()
        Mu["Umandater"][i] += 1
        n = int(Mu["Umandater"][i])
        stemmetall[i] = upartisum[i] / (deletall[n])

    diffU = (
        Mu["Umandater"] - M.sum(axis=1)[upartier]
    )  # antall utgjevningsmand per parti

    if all(diffU >= 0):  # bryter hvis ingen parti er overrepresentert
        overrep = False

    else:
        overrep_partier = diffU[diffU < 0].index  # partiene som er overrepresentert
        upartier = np.array([p for p in upartier if p not in overrep_partier])

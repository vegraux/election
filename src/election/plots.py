import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from election.nation import Nation

LEFT = ()

LEFT_OR_RIGHT = dict(zip(['A', 'FRP', 'H', 'KRF', 'MDG', 'PF', 'RØDT', 'SP', 'SV', 'V'],
                         ["Rødgrønn","Promp","Promp","Promp","Rødgrønn","Random","Rødgrønn","Rødgrønn","Rødgrønn", "Promp"]))

def stack_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.stack().reset_index().rename(columns={0: "representatives"})


def get_representatives_per_party(nation: Nation) -> go.Figure:
    fig = px.bar(stack_data(nation.party_representatives), x="party", y="representatives", color="district")
    return fig


def get_left_vs_right(nation: Nation, group: bool = True) -> go.Figure:
    df = stack_data(nation.party_representatives)
    df["side"] = df["party"].map(LEFT_OR_RIGHT)
    kwargs = {"color" : "party"} if group else {}
    fig = px.bar(df, x="side", y="representatives", **kwargs)

    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(df["side"].unique())-0.5,
        y0=85, y1=85,
        line=dict(color="red", width=2),
        xref="x", yref="y"
    )
    return fig


def get_representatives_per_district(nation: Nation) -> go.Figure:
    fig = px.bar(stack_data(nation.party_representatives), x="district", y="representatives", color="party")
    return fig


def get_needed_votes(nation: Nation) -> go.Figure:
    df = nation.needed_votes_to_last_rep.sort_values(by="votes_needed").head(20)
    df["parti"] = df.apply(lambda x: f"{x.party} ({x.district})", axis=1)
    fig = px.bar(df, y="parti", x="votes_needed")
    return fig

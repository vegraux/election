import dash
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
import dash_daq as daq

from flask import Flask

from election.examples.election_2021 import norway
from election.plots import get_needed_votes, get_representatives_per_district, get_representatives_per_party, \
    get_left_vs_right


def create_app(debug: bool = False) -> Flask:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

    layout = html.Div(
        [
            dbc.Row(dbc.Col(html.H1(id="header-1", children="Stortingsvalg"))),
            html.Br(),
            html.Br(),
            dbc.Row(
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H6("Stuff", className="card-title"),
                            dbc.Button("Refresh", id="refresh-btn", color="primary", n_clicks=0),
                            #daq.BooleanSwitch(id='my-boolean-switch', on=True, label="Grupper data", labelPosition="top"),

                        ]
                    )
                )
            ),
            dbc.Row(dbc.Col(html.H3(id="header-0", children="Mandater for høyre-og venstresida"))),
            dcc.Graph(id="reps-per-side"),
            html.Br(),


            dbc.Row(dbc.Col(html.H3(id="header-2", children="Representanter per parti"))),
            dcc.Graph(id="reps-per-party-fig"),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(id="header-3", children="Representanter per distrikt"))),
            dcc.Graph(id="reps-per-district-fig"),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(id="heade-4", children="Partier nærmest siste mandat"))),
            dcc.Graph(id="needed-votes-fig"),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(id="header-5", children="Kampen om siste mandat per distrikt"))),
            dash_table.DataTable(id="data-table"),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(id="header-6", children="Prosentvis oppslutning"))),
            dash_table.DataTable(id="oppslutning-table"),
            html.Br(),
        ]
    )

    app.layout = dbc.Container(layout)


    @app.callback(
        Output("reps-per-side", "figure"),
        Input("refresh-btn", "n_clicks"),
         #Input('my-boolean-switch', 'on')
    )
    def get_side_figure(_) -> go.Figure:
        return get_left_vs_right(norway)

    @app.callback(
        Output("reps-per-party-fig", "figure"),
        Input("refresh-btn", "n_clicks"),
    )
    def get_reps_per_party(_) -> go.Figure:
        return get_representatives_per_party(norway)

    @app.callback(
        Output("reps-per-district-fig", "figure"),
        Input("refresh-btn", "n_clicks"),
    )
    def get_reps_per_district(_) -> go.Figure:
        return get_representatives_per_district(norway)

    @app.callback(
        Output("needed-votes-fig", "figure"),
        Input("refresh-btn", "n_clicks"),
    )
    def get_need_votes(_) -> go.Figure:
        return get_needed_votes(norway)

    @app.callback(
        Output("data-table", "data"),
        Output("data-table", "columns"),
        Input("refresh-btn", "n_clicks"),
    )
    def update_table(_):
        df = norway.representatives_per_party.query("remaining_representative == 0.0")
        closest_per_district = norway.needed_votes_to_last_rep.groupby("district")["votes_needed"].idxmin()
        df = (
            df.merge(
                norway.needed_votes_to_last_rep.loc[closest_per_district].rename(columns={"party": "Closest party"}),
                left_on="district",
                right_on="district",
            )
            .reset_index()
            .sort_values("votes_needed")
        )
        use = ["district", "name", "Closest party", "votes_needed"]
        data = df[use].to_dict("records")
        columns = [{"name": i, "id": i} for i in use]
        return data, columns

    @app.callback(
        Output("oppslutning-table", "data"),
        Output("oppslutning-table", "columns"),
        Input("refresh-btn", "n_clicks"),
    )
    def update_oppslutning(_):
        df = norway.party_percentage
        data = df.to_dict("records")
        columns = [{"name": i, "id": i} for i in df.columns]
        return data, columns


    if debug:
        app.run(host="0.0.0.0", port=9090)

    return app.server


if __name__ == "__main__":
    create_app(debug=True)

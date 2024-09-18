"""
Purpose: A manager for the dashboard.
"""

from dash import Dash, html, dcc, get_asset_url
import dash_bootstrap_components as dbc
import pandas as pd

class DashBoardManager:
    def __init__(self, flask_app):
        self.dashboard = Dash(
            __name__, 
            server=flask_app, 
            url_base_pathname="/", 
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        self.dashboard.title = "The Daily BTC"
        self.dashboard._favicon = "favicon.ico"
        self.statuses_df = None
        self.news_df = None
        return None
    
    def update_datasets(self, data_objects):
        self.statuses_df = pd.DataFrame(data_objects['statuses'])
        self.statuses_df["last_updated_date"] = pd.to_datetime(self.statuses_df["last_updated_date"])
        self.news_df = pd.DataFrame(data_objects['news'])
        fig_line_columns = [
            "last_updated_date", "price_usd", "market_cap_usd", 
            "fully_diluted_valuation_usd", "total_volume_usd"
        ]
        print("\n\n")
        print(self.statuses_df[fig_line_columns].groupby("last_updated_date").mean())
        exit()
        # fig_line = px.line(self.statuses_df[fig_line_columns].groupby("last_updated_date").mean(), x="last_updated_date", y="price_usd")
        print("\n", "HERE 2:", len(self.statuses_df), "|", len(self.news_df), "\n")
        return None

    def update_dashboard(self):
        self.dashboard.layout = html.Div(
            [
                # HEADER SECTION
                html.Div(
                    [
                        html.H1(
                            [
                                "The Daily BTC", 
                                html.Img(src=get_asset_url("bitcoin-icon-small.webp"), className="ps-2")
                            ]
                        )
                    ], 
                    className="row p-2 text-center"
                ),
                # HEADLINE SECTION
                html.Div(
                    [
                        html.P(
                            [
                                html.Span(f"MARKET CAP RANK: #{self.statuses_df.loc[0, 'market_cap_rank']}"),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"ATH PRICE: ${self.statuses_df.loc[0, 'ath_usd']} ON {self.statuses_df.loc[0, 'ath_date']}"),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"ATL PRICE: ${self.statuses_df.loc[0, 'atl_usd']} ON {self.statuses_df.loc[0, 'atl_date']}")
                            ]
                        )
                    ], 
                    className="row text-center"
                ),
                # NEWS & CHARTS SECTION
                html.Div(
                    [
                        # SOCIAL & ECONOMIC CHARTS SECTION
                        html.Div(
                            [
                                # ECONOMIC CHARTS SECTION
                                html.Div(
                                    [
                                        html.P("ECONOMIC CHARTS"),
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    label='PRICES', 
                                                    children=None, 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                                dcc.Tab(
                                                    label='MARKET CAPS', 
                                                    children=None, 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                                dcc.Tab(
                                                    label='TOTAL VOLUMES', 
                                                    children=None, 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                )
                                            ], 
                                            style={"height": "5vh"}
                                        )
                                    ], 
                                    className="row-8 p-4"
                                ),
                                # SOCIAL CHARTS SECTION
                                html.Div(
                                    [
                                        html.P("SOCIAL CHARTS"),
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    label='GITHUB', 
                                                    children=None, 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                            ),
                                                dcc.Tab(
                                                    label='TWITTER', 
                                                    children=None, 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                            ], 
                                            style={"height": "5vh"}
                                        )
                                    ], 
                                    className="row-4 p-4"
                                )
                            ], 
                            className="col-8"
                        ),
                        # NEWS SECTION
                        html.Div(
                                [
                                    html.P("MAJOR NEWS")
                                ], 
                            className="col-4 p-4"
                        )
                    ], 
                    className="row"
                ),
            ], 
            className="container-fluid vh-100 bg-dark text-white"
        )
        return None

    def update(self, data_objects):
        self.update_datasets(data_objects)
        self.update_dashboard()
        return None

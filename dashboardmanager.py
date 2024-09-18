"""
Purpose: A manager for the dashboard.
"""

from dash import Dash, html, dcc, callback, Output, Input, get_asset_url
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

class DashBoardManager:
    def __init__(self, flask_app):
        self.dashboard = Dash(__name__, 
                              server=flask_app, 
                              url_base_pathname="/", 
                              external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.dashboard.title = "The Daily BTC"
        self.dashboard._favicon = "favicon.ico"
        self.statuses_df = None
        self.news_df = None
        return None
    
    def update_datasets(self, data_objects):
        self.statuses_df = pd.DataFrame(data_objects['statuses'])
        self.news_df = pd.DataFrame(data_objects['news'])
        print("\n", "HERE 2:", len(self.statuses_df), "|", len(self.news_df), "\n")
        return None

    def update_dashboard(self):
        self.dashboard.layout = html.Div([
            html.Div([
                html.H1([
                    "The Daily BTC", 
                    html.Img(src=get_asset_url("bitcoin-icon-small.webp"), 
                             className="ps-2")
                    ])
                ], className="row pt-2 pb-2 text-center"),
            html.Div([
                html.P(f"""ATH: ${self.statuses_df.loc[0, 'ath_usd']} ON {self.statuses_df.loc[0, 'ath_date']}
                            {" " * 5}|{" " * 5}
                            ATL: ${self.statuses_df.loc[0, 'atl_usd']} ON {self.statuses_df.loc[0, 'atl_date']}""")
                ], className="row text-center"),
            html.Div([
                html.Div([
                    html.Div([
                        html.P("PRICE VS TIME")
                        ], className="row-8"),
                    html.Div([
                        html.P("GITHUB DEVELOPMENT")
                        ], className="row-4")
                    ], className="col-8"),
                html.Div([html.P("MAJOR NEWS")
                    ], className="col-4")
                ], className="row"),
            ], className="container-fluid vh-100 bg-dark text-white")
        return None

    def update(self, data_objects):
        self.update_datasets(data_objects)
        self.update_dashboard()
        return None

"""
Purpose: A manager for the dashboard.
"""

from dash import Dash, html, dcc, get_asset_url
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

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
        return None
    
    def update_datasets(self, data_objects):
        statuses_df = pd.DataFrame(data_objects['statuses'])
        statuses_df["last_updated_date"] = pd.to_datetime(statuses_df["last_updated_date"])
        news_df = pd.DataFrame(data_objects['news'])

        fig_columns = [
            "last_updated_date", 
            "price_usd", "market_cap_usd", "fully_diluted_valuation_usd", "total_volume_usd",
            "twitter_followers_count", "github_total_issues_count", "github_closed_issues_count",
            "github_pull_requests_merged_count", "github_pull_request_contributors_count"
        ]
        fig_df = (statuses_df[fig_columns].groupby("last_updated_date").mean().sort_index().reset_index()
                  .astype({"github_total_issues_count": int, "github_closed_issues_count": int}))
        fig_df["price_ema50_usd"] = fig_df["price_usd"].ewm(span=50, adjust=False).mean()
        fig_df["price_ema200_usd"] = fig_df["price_usd"].ewm(span=200, adjust=False).mean()
        fig_df["twitter_followers_markers_size"] = (
            fig_df["twitter_followers_count"] * (100 - 10) / 
            (max(fig_df["twitter_followers_count"]) - min(fig_df["twitter_followers_count"]))
            if (max(fig_df["twitter_followers_count"]) - min(fig_df["twitter_followers_count"])) > 0 
            else [10] * len(fig_df["twitter_followers_count"])
        )

        # ECONOMICS
        fig_prices = go.Figure()
        fig_prices.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["price_usd"],
                line={"color": "red"},
                marker={"size": 12},
                mode='lines+markers',
                name="SPOT"
            )
        )
        fig_prices.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["price_ema50_usd"],
                line={"color": "yellow", "dash": "dot"},
                marker={"size": 12},
                mode='lines+markers',
                name="EMA 50"
            )
        )
        fig_prices.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["price_ema200_usd"],
                line={"color": "orange", "dash": "dash"},
                marker={"size": 12},
                mode='lines+markers',
                name="EMA 200"
            )
        )
        fig_prices.update_layout(
            {
                "xaxis_title": "DATE", 
                "yaxis_title": "AVERAGE PRICE ($)"
            }
        )

        fig_market_caps = go.Figure()
        fig_market_caps.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], y=fig_df["market_cap_usd"], 
                line={"color": "red"},
                marker={"size": 12},
                mode='lines+markers', 
                name="IN CIRCULATION"
            )
        )
        fig_market_caps.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], y=fig_df["fully_diluted_valuation_usd"], 
                line={"color": "springgreen"},
                marker={"size": 12},
                mode='lines+markers',
                name="FULLY DILUTED"
            )
        )
        fig_market_caps.update_layout(
            {
                "xaxis_title": "DATE", 
                "yaxis_title": "AVERAGE MARKET CAP ($)"
            }
        )

        fig_total_volumes = go.Figure()
        fig_total_volumes.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["total_volume_usd"],
                line={"color": "red"},
                marker={"size": 12},
                mode='lines+markers'
            )
        )
        fig_total_volumes.update_layout(
            {
                "xaxis_title": "DATE", 
                "yaxis_title": "AVERAGE TOTAL VOLUME ($)"
            }
        )

        # SOCIALS
        print(fig_df["github_total_issues_count"].iloc[-1])
        fig_github = go.Figure()
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_total_issues_count"],
                line={"color": "red"},
                marker={"size": 12},
                mode='lines+markers',
            )
        )
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_closed_issues_count"],
                line={"color": "springgreen"},
                marker={"size": 12},
                mode='lines+markers',
            )
        )
        fig_github.update_layout(
            xaxis = {
                "showline": True,
                "showgrid": False,
                "showticklabels": True,
                "title": "DATE"
            },
            yaxis = {
                "showgrid": False,
                "zeroline": False,
                "showline": False,
                "showticklabels": False,
            },
            title_text = "TOTAL COUNT OF ISSUES",
            title_x = 0.5,
            showlegend = False,
            annotations = [
                {
                    "xref": "paper",
                    "x": 0.95,
                    "y": fig_df["github_total_issues_count"].iloc[-1],
                    "text": f"OPENED: {fig_df["github_total_issues_count"].iloc[-1]}",
                    "font": {"color": "red"}
                },
                {
                    "xref": "paper",
                    "x": 0.95,
                    "y": fig_df["github_closed_issues_count"].iloc[-1],
                    "text": f"CLOSED: {fig_df["github_closed_issues_count"].iloc[-1]}",
                    "font": {"color": "springgreen"}
                }
            ]
        )

        fig_twitter = go.Figure()
        fig_twitter.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["twitter_followers_count"],
                marker={
                    "color": fig_df["twitter_followers_count"].to_list(), 
                    "size": fig_df["twitter_followers_markers_size"].to_list(),
                    "showscale": True
                },
                mode='markers'
            )
        )
        fig_twitter.update_layout(
            xaxis = {
                "showline": True,
                "showgrid": False,
                "title": "DATE", 
            },
            yaxis = {
                "showgrid": False,
                "showticklabels": False,
            },
            title_text = "TOTAL COUNT OF FOLLOWERS",
            title_x = 0.5
        )

        for fig_object in [fig_prices, fig_market_caps, fig_total_volumes, fig_github, fig_twitter]:
            fig_object.update_layout(
                {
                    "plot_bgcolor": "darkslategray", 
                    "paper_bgcolor": "darkslategray", 
                    "font_color": "white",
                }
            )

        dash_objects = {
            "headline": {
                "market_cap": statuses_df.loc[0, 'market_cap_rank'],
                "ath_usd": statuses_df.loc[0, 'ath_usd'],
                "ath_date": statuses_df.loc[0, 'ath_date'],
                "atl_usd": statuses_df.loc[0, 'atl_usd'],
                "atl_date": statuses_df.loc[0, 'atl_date']
            },
            "economics": {
                "prices": fig_prices,
                "market_caps": fig_market_caps,
                "total_volumes": fig_total_volumes
            },
            "socials": {
                "github": fig_github,
                "twitter": fig_twitter
            }
        }

        print("\n", "HERE 2:", len(statuses_df), "|", len(news_df), "\n")

        return dash_objects

    def update_dashboard(self, dash_objects):
        self.dashboard.layout = html.Div(
            [
                # HEADER SECTION
                html.Div(
                    [
                        html.H1(
                            [
                                "The Daily BTC", 
                                html.Img(src=get_asset_url("bitcoin-icon-small.webp"), className="p-2")
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
                                html.Span(f"MARKET CAP RANK: #{dash_objects["headline"]["market_cap"]}"),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"ATH PRICE: ${dash_objects["headline"]["ath_usd"]} ON {dash_objects["headline"]["ath_date"]}"),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"ATL PRICE: ${dash_objects["headline"]["atl_usd"]} ON {dash_objects["headline"]["atl_date"]}")
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
                                                    dcc.Graph(
                                                        figure=dash_objects["economics"]["prices"],
                                                        style={"width": "100%"}
                                                    ),
                                                    label='PRICES', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#227B94"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=dash_objects["economics"]["market_caps"],
                                                        style={"width": "100%"}
                                                    ),
                                                    label='MARKET CAPS', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#227B94"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=dash_objects["economics"]["total_volumes"],
                                                        style={"width": "100%"}
                                                    ),
                                                    label='TOTAL VOLUMES', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#227B94"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                )
                                            ], 
                                            style={"height": "5vh"}
                                        )
                                    ], 
                                    className="col"
                                ),
                                # SOCIAL CHARTS SECTION
                                html.Div(
                                    [
                                        html.P("SOCIAL CHARTS"),
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=dash_objects["socials"]["github"],
                                                        style={"width": "100%"}
                                                    ),
                                                    label='GITHUB', 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#227B94"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                            ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=dash_objects["socials"]["twitter"],
                                                        style={"width": "100%"}
                                                    ),
                                                    label='TWITTER', 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#227B94"},
                                                    selected_style={
                                                        "backgroundColor": "#78B7D0", 
                                                        "borderTop": "1vh solid white"
                                                    }
                                                ),
                                            ], 
                                            style={"height": "5vh"}
                                        )
                                    ], 
                                    className="col pt-4"
                                )
                            ], 
                            className="col-8 ps-4 pe-4"
                        ),
                        # NEWS SECTION
                        html.Div(
                                [
                                    html.P("MAJOR NEWS")
                                ], 
                            className="col-4 ps-4 pe-4"
                        )
                    ], 
                    className="row ps-4 pe-4 pt-2 pb-2"
                ),
                # FOOTER SECTION
                html.Div(
                    [
                        html.Span("For demonstration purposes only; not for commercial use."),
                        html.Br(),
                        html.Span("Data courtesy of CoinGecko and News API."),
                        html.Br(),
                        html.Span(
                            [
                                html.A(
                                    html.Img(src=get_asset_url("linkedin_icon.png"), className="p-2", style={"width": "6vh"}), 
                                    href="https://www.linkedin.com/in/tamleauthentic/",
                                ),
                                html.A(
                                    html.Img(src=get_asset_url("github_icon.png"), className="p-2", style={"width": "6vh"}),
                                    href="https://github.com/moodysquirrelapps",
                                )
                            ]
                        )
                    ], 
                    className="row p-4",
                    style={
                        "fontStyle": "italic",
                        "fontSize": "10pt",
                        "textAlign": "right",
                        "justify-content": "right"
                    }
                ),
            ], 
            className="container-fluid bg-dark text-white"
        )
        return None

    def update(self, data_objects):
        dash_objects = self.update_datasets(data_objects)
        self.update_dashboard(dash_objects)
        return None

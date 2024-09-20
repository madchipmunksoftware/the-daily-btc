"""
Purpose: A dashboard manager for The Daily BTC Web Application.
"""

from dash import Dash, html, dcc, get_asset_url
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from transformers import pipeline

class DashBoardManager:
    def __init__(self, special_name_main_script):
        self.dashboard = Dash(
            special_name_main_script, 
            external_stylesheets=[dbc.themes.BOOTSTRAP]
            )
        self.dashboard.title = "The Daily BTC"
        self.dashboard._favicon = "favicon.ico"
        self.sentiment_pipeline = pipeline(
            task="sentiment-analysis", 
            model="cardiffnlp/twitter-roberta-base-sentiment"
            )
        self.news_df = pd.DataFrame()
        self.news_empty_post = {
            "source_name": "",
            "author": "",
            "title": "",
            "subtitle": "",
            "url_to_post": "",
            "url_to_image": "",
            "published_date": ""
            }
        return None
    
    def update_datasets(self, data_objects):
        # ECONOMICS & SOCIALS CALCULATIONS
        statuses_df = pd.DataFrame(data_objects['statuses']).dropna()
        statuses_df["last_updated_date"] = pd.to_datetime(statuses_df["last_updated_date"])
        fig_columns = [
            "last_updated_date", 
            "price_usd", "market_cap_usd", "fully_diluted_valuation_usd", "total_volume_usd",
            "twitter_followers_count", "github_total_issues_count", "github_closed_issues_count",
            "github_pull_requests_merged_count", "github_pull_request_contributors_count"
            ]
        fig_df = (
            statuses_df[fig_columns].groupby("last_updated_date")
            .agg(
                {
                    "price_usd": "mean",
                    "market_cap_usd": "mean",
                    "fully_diluted_valuation_usd": "mean",
                    "total_volume_usd": "mean",
                    "twitter_followers_count": "max",
                    "github_total_issues_count": "max",
                    "github_closed_issues_count": "max",
                    "github_pull_requests_merged_count": "max", 
                    "github_pull_request_contributors_count": "max"
                    }
                ).sort_index().reset_index()
            )
        fig_df["price_ema50_usd"] = fig_df["price_usd"].ewm(span=50, adjust=False).mean()
        fig_df["price_ema200_usd"] = fig_df["price_usd"].ewm(span=200, adjust=False).mean()

        # ECONOMICS PLOTS
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
            xaxis={"title": "DATE"},
            yaxis={"range": [min(fig_df["price_usd"]) * 0.95, max(fig_df["price_usd"]) * 1.05]},
            title={"text": "DAILY AVERAGE PRICE ($)", "x": 0.5}
            )

        fig_market_caps = go.Figure()
        fig_market_caps.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["market_cap_usd"], 
                line={"color": "red"},
                marker={"size": 12},
                mode='lines+markers', 
                name="IN CIRCULATION"
                )
            )
        fig_market_caps.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["fully_diluted_valuation_usd"], 
                line={"color": "springgreen"},
                marker={"size": 12},
                mode='lines+markers',
                name="FULLY DILUTED"
                )
            )
        fig_market_caps.update_layout(
            xaxis={"title": "DATE"},
            yaxis={
                "range": [
                    min(fig_df["market_cap_usd"]) * 0.95, 
                    max(fig_df["fully_diluted_valuation_usd"]) * 1.05
                    ]
                },
            title={"text": "DAILY AVERAGE MARKET CAP ($)", "x": 0.5}
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
            xaxis={"title": "DATE"},
            yaxis={
                "range": [
                    min(fig_df["total_volume_usd"]) * 0.95, 
                    max(fig_df["total_volume_usd"]) * 1.05
                    ]
                },
            title={"text": "DAILY AVERAGE TOTAL VOLUME ($)", "x": 0.5}
            )

        # SOCIALS PLOTS
        fig_github = go.Figure()
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_total_issues_count"],
                mode="lines+text",
                line={"color": "red"},
                text=fig_df["github_total_issues_count"].astype("str"),
                textfont={"color": "red"},
                textposition="top center",
                name="OPENED",
                fill='tozeroy'
                )
            )
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_closed_issues_count"],
                mode="lines+text",
                line={"color": "springgreen"},
                text=fig_df["github_closed_issues_count"].astype("str"),
                textfont={"color": "springgreen"},
                textposition="bottom center",
                name="CLOSED",
                fill='tozeroy'
                )
            )
        fig_github.update_layout(
            xaxis={"showgrid": False, "title": "DATE"},
            yaxis={"showgrid": False, "showticklabels": False},
            title = {"text": "DAILY COUNT OF ISSUES", "x": 0.5}
            )

        fig_twitter = go.Figure()
        fig_twitter.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["twitter_followers_count"],
                mode='markers',
                marker={"color": "yellow", "size": 12}
                )
            )
        fig_twitter.update_layout(
            xaxis={"showline": True, "showgrid": False, "title": "DATE" },
            yaxis={
                "range": [
                    min(fig_df["twitter_followers_count"]) * 0.95, 
                    max(fig_df["twitter_followers_count"]) * 1.05
                    ]
                },
            title={"text": "DAILY COUNT OF FOLLOWERS", "x": 0.5}
            )

        # GENERAL PLOTS STYLINGS
        for fig_object in [fig_prices, fig_market_caps, fig_total_volumes, fig_github, fig_twitter]:
            fig_object.update_layout(
                {
                    "plot_bgcolor": "darkslategray", 
                    "paper_bgcolor": "darkslategray", 
                    "font_color": "white",
                    },
                xaxis = {
                    "tickformat": "%b %d, %Y",
                    "tickangle": 90,
                    "dtick": 86400000,
                    "range": [
                        min(fig_df["last_updated_date"]) - pd.DateOffset(days=1), 
                        max(fig_df["last_updated_date"]) + pd.DateOffset(days=1)
                        ]
                    }
                )

        # NEWS CALCULATIONS
        if len(self.news_df) > 0:
            news_df_temp = pd.DataFrame(data_objects['news']).dropna()
            news_df_temp = (
                news_df_temp.loc[[news_id not in self.news_df["id"].to_list() for news_id in news_df_temp['id']]]
                )
            if len(news_df_temp) > 0:
                news_df_temp["published_date"] = pd.to_datetime(news_df_temp["published_date"])
                news_df_temp["subtitle"] = (
                    "By "+ news_df_temp["author"] + 
                    " on " + news_df_temp["published_date"].dt.strftime("%b %d, %Y")
                    )
                news_df_temp["content_preview"] = (
                    "Title: " + news_df_temp["title"] + 
                    " Description: " + news_df_temp["description"]
                    )
                results = (
                    pd.DataFrame(self.sentiment_pipeline(news_df_temp["content_preview"].to_list()))
                    .rename(columns={"label": "sentiment_label", "score": "sentiment_score"})
                    .replace({"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"})
                    )
                news_df_temp = pd.concat(
                    [news_df_temp.reset_index(drop=True), results.reset_index(drop=True)], 
                    axis="columns",
                    )
                self.news_df = pd.concat(
                    [self.news_df.reset_index(drop=True), news_df_temp.reset_index(drop=True)], 
                    axis="index", 
                    ignore_index=True
                    )
        else:
            self.news_df = pd.DataFrame(data_objects['news']).dropna()
            self.news_df["published_date"] = pd.to_datetime(self.news_df["published_date"])
            self.news_df["subtitle"] = (
                "By "+ self.news_df["author"] + 
                " on " + self.news_df["published_date"].dt.strftime("%b %d, %Y")
                )
            self.news_df["content_preview"] = (
                "Title: " + self.news_df["title"] + 
                " Description: " + self.news_df["description"]
                )
            results = (
                pd.DataFrame(self.sentiment_pipeline(self.news_df["content_preview"].to_list()))
                .rename(columns={"label": "sentiment_label", "score": "sentiment_score"})
                .replace({"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"})
                )
            self.news_df = pd.concat(
                [self.news_df.reset_index(drop=True), results.reset_index(drop=True)], 
                axis="columns"
                )
        
        news_today = (
            self.news_df[self.news_df["published_date"] == pd.to_datetime(pd.Timestamp('now').date())]
            .sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if (self.news_df["published_date"] == pd.to_datetime(pd.Timestamp('now').date())).any()
            else self.news_empty_post
            )
        news_this_week = (
            self.news_df[
                (self.news_df["published_date"] < pd.to_datetime(pd.Timestamp('now').date())) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=7)))
                ].sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if ((self.news_df["published_date"] < pd.to_datetime(pd.Timestamp('now').date())) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=7)))).any()
            else self.news_empty_post
            )
        news_this_month = (
            self.news_df[
                (self.news_df["published_date"] < pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=7))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=30)))
                ].sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if ((self.news_df["published_date"] < pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=7))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp('now').date() - pd.DateOffset(days=30)))).any()
            else self.news_empty_post
            )

        # DASHBOARD OBJECTS
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
                },
            "news": {
                "today": news_today,
                "this_week": news_this_week,
                "this_month": news_this_month
                }
            }
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
                                html.Span(f"""ALL-TIME HIGH PRICE: ${dash_objects["headline"]["ath_usd"]} 
                                          ON {dash_objects["headline"]["ath_date"]}"""),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"""ALL-TIME LOW PRICE: ${dash_objects["headline"]["atl_usd"]} 
                                          ON {dash_objects["headline"]["atl_date"]}""")
                                ]
                            )
                        ], 
                    className="row text-center"
                    ),
                # NEWS & CHARTS SECTION
                html.Div(
                    [
                        html.Div( # SOCIAL & ECONOMIC CHARTS SECTION
                            [
                                html.Div( # ECONOMIC CHARTS SECTION
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
                                                    style={"backgroundColor": "#16325B"},
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
                                                    style={"backgroundColor": "#16325B"},
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
                                    className="col"
                                    ),
                                html.Div( # SOCIAL CHARTS SECTION
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
                                                    style={"backgroundColor": "#16325B"},
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
                                    className="col pt-4"
                                    )
                                ], 
                            className="col-8 ps-4 pe-4"
                            ),
                        html.Div( # NEWS SECTION
                            [
                                html.P("MAJOR NEWS"),
                                html.Div( # TODAY POST
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P(
                                                            "TODAY", 
                                                            className="text-center", 
                                                            style={"backgroundColor": "red"}
                                                            ),
                                                        html.P(
                                                            [
                                                                html.Div(
                                                                    html.Img(
                                                                        src=dash_objects["news"]["today"]["url_to_image"], 
                                                                        className="mx-auto w-100",
                                                                        ),
                                                                    className="d-flex align-items-center"
                                                                    ),
                                                                html.A(
                                                                    dash_objects["news"]["today"]["title"], 
                                                                    href=dash_objects["news"]["today"]["url_to_post"],
                                                                    target="_blank",
                                                                    rel="noopener noreferrer"
                                                                    ),
                                                                html.Br(),
                                                                html.Span(
                                                                    dash_objects["news"]["today"]["subtitle"], 
                                                                    style={"fontStyle": "italic"}
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                    className="col ps-2 pe-2 pt-2"
                                                    )
                                                ],
                                            className="row border rounded"
                                            ),
                                        ],
                                    className="col ps-2 pe-2 pb-4"
                                    ),
                                html.Div( # THIS WEEK POST
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P(
                                                            "THIS WEEK", 
                                                            className="text-center", 
                                                            style={"backgroundColor": "red"}
                                                            ),
                                                        html.P(
                                                            [
                                                                html.Div(
                                                                    html.Img(
                                                                        src=dash_objects["news"]["this_week"]["url_to_image"], 
                                                                        className="mx-auto w-100",
                                                                        ),
                                                                    className="d-flex align-items-center"
                                                                    ),
                                                                html.A(
                                                                    dash_objects["news"]["this_week"]["title"], 
                                                                    href=dash_objects["news"]["this_week"]["url_to_post"],
                                                                    target="_blank",
                                                                    rel="noopener noreferrer"
                                                                    ),
                                                                html.Br(),
                                                                html.Span(
                                                                    dash_objects["news"]["this_week"]["subtitle"], 
                                                                    style={"fontStyle": "italic"}
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                    className="col ps-2 pe-2 pt-2"
                                                    )
                                                ],
                                            className="row border rounded"
                                            ),
                                        ],
                                    className="col ps-2 pe-2 pb-4"
                                    ),
                                html.Div(  # THIS MONTH POST
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P(
                                                            "THIS MONTH", 
                                                            className="text-center", 
                                                            style={"backgroundColor": "red"}
                                                            ),
                                                        html.P(
                                                            [
                                                                html.Div(
                                                                    html.Img(
                                                                        src=dash_objects["news"]["this_month"]["url_to_image"], 
                                                                        className="mx-auto w-100",
                                                                        ),
                                                                    className="d-flex align-items-center"
                                                                    ),
                                                                html.A(
                                                                    dash_objects["news"]["this_month"]["title"], 
                                                                    href=dash_objects["news"]["this_month"]["url_to_post"],
                                                                    target="_blank",
                                                                    rel="noopener noreferrer"
                                                                    ),
                                                                html.Br(),
                                                                html.Span(
                                                                    dash_objects["news"]["this_month"]["subtitle"], 
                                                                    style={"fontStyle": "italic"}
                                                                    )
                                                                ]
                                                            )
                                                        ],
                                                    className="col ps-2 pe-2 pt-2"
                                                    )
                                                ],
                                            className="row border rounded"
                                            ),
                                        ],
                                    className="col ps-2 pe-2 pb-4"
                                    ),
                                ], 
                            className="col-4 ps-4 pe-4"
                            )
                        ], 
                    className="row ps-4 pe-4 pt-2 pb-2"
                    ),
                html.Div( # FOOTER SECTION
                    [
                        html.Span("For demonstration purposes only; not for commercial use."),
                        html.Br(),
                        html.Span("Data courtesy of CoinGecko and News API."),
                        html.Br(),
                        html.Span(
                            [
                                html.A(
                                    html.Img(
                                        src=get_asset_url("linkedin_icon.png"), 
                                        className="p-2", 
                                        style={"width": "6vh"}
                                        ), 
                                    href="https://www.linkedin.com/in/tamleauthentic/",
                                    ),
                                html.A(
                                    html.Img(
                                        src=get_asset_url("github_icon.png"), 
                                        className="p-2", 
                                        style={"width": "6vh"}
                                        ),
                                    href="https://github.com/moodysquirrelapps",
                                    )
                                ]
                            )
                        ], 
                    className="row p-4",
                    style={"fontStyle": "italic", "fontSize": "11pt", "textAlign": "right", "justify-content": "right"}
                    ),
                ], 
            className="container-fluid bg-dark text-white"
            )
        return None

    def update(self, data_objects):
        dash_objects = self.update_datasets(data_objects)
        self.update_dashboard(dash_objects)
        return None

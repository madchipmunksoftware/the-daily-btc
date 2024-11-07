"""
Purpose: A dashboard manager for The Daily BTC Web Application.
"""

from dash import Dash, html, dcc, get_asset_url
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from transformers import pipeline

class DashBoardManager:
    def __init__(self, app, data_objects):
        # Parameters
        self.dashboard = Dash(
            server=app,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            routes_pathname_prefix="/home/"
            )
        self.dashboard.title = "The Daily BTC"
        self.dashboard._favicon = "favicon.ico"

        # Calculations
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

        # Layout
        self.dash_objects = self.get_dash_objects(data_objects)
        self.dashboard.layout = self.get_dash_layout
        return None
    
    def get_dash_objects(self, data_objects):
        # Economic & Social Charts Calculations
        statuses_df = pd.DataFrame(data_objects['statuses']).dropna()
        statuses_df["last_updated_date"] = pd.to_datetime(statuses_df["last_updated_date"], utc=True)
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

        # Economic Charts Designs
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
                line={"color": "lime", "dash": "dash"},
                marker={"size": 12},
                mode='lines+markers',
                name="EMA 200"
                )
            )
        fig_prices.update_layout(
            xaxis={"showline": True, "showgrid": False, "title": "DATE"},
            yaxis={
                "showline": True, 
                "showgrid": False, 
                "range": [min(fig_df["price_usd"]) * 0.95, max(fig_df["price_usd"]) * 1.05]
                },
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
                line={"color": "yellow"},
                marker={"size": 12},
                mode='lines+markers',
                name="FULLY DILUTED"
                )
            )
        fig_market_caps.update_layout(
            xaxis={"showline": True, "showgrid": False, "title": "DATE"},
            yaxis={
                "showline": True,
                "showgrid": False,
                "range": [
                    min(fig_df["market_cap_usd"]) * 0.95, 
                    max(fig_df["fully_diluted_valuation_usd"]) * 1.05
                    ]
                },
            title={"text": "DAILY AVERAGE MARKET CAP ($)", "x": 0.5}
            )

        fig_total_volumes = go.Figure()
        fig_total_volumes.add_trace(
            go.Bar(
                x=fig_df["last_updated_date"], 
                y=fig_df["total_volume_usd"],
                marker={"color": "lime"},
                )
            )
        fig_total_volumes.update_layout(
            xaxis={"title": "DATE"},
            yaxis={"range": [0, max(fig_df["total_volume_usd"]) * 1.05]},
            title={"text": "DAILY AVERAGE TOTAL VOLUME ($)", "x": 0.5}
            )

        # Social Charts Designs
        fig_github = go.Figure()
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_total_issues_count"],
                mode="lines",
                line={"color": "red"},
                name="OPENED",
                fill='tozeroy'
                )
            )
        fig_github.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["github_closed_issues_count"],
                mode="lines",
                line={"color": "lime"},
                name="CLOSED",
                fill='tozeroy'
                )
            )
        fig_github.add_trace(
            go.Scatter(
                x=[fig_df["last_updated_date"].tolist()[-1]], 
                y=[fig_df["github_total_issues_count"].tolist()[-1]],
                mode="lines+text",
                line={"color": "red"},
                text=[f"{fig_df['github_total_issues_count'].tolist()[-1]:,}"],
                textfont={"color": "red", "size": 12},
                textposition="middle right",
                showlegend=False
                )
            )
        fig_github.add_trace(
            go.Scatter(
                x=[fig_df["last_updated_date"].tolist()[-1]], 
                y=[fig_df["github_closed_issues_count"].tolist()[-1]],
                mode="lines+text",
                line={"color": "lime"},
                text=[f"{fig_df['github_closed_issues_count'].tolist()[-1]:,}"],
                textfont={"color": "lime", "size": 12},
                textposition="middle right",
                showlegend=False
                )
            )
        fig_github.update_layout(
            xaxis={"showgrid": False, "title": "DATE"},
            yaxis={"showgrid": False, "showticklabels": False},
            title = {"text": "DAILY TOTAL NUMBER OF ISSUES", "x": 0.5}
            )

        fig_twitter = go.Figure()
        fig_twitter.add_trace(
            go.Scatter(
                x=fig_df["last_updated_date"], 
                y=fig_df["twitter_followers_count"],
                mode='markers',
                marker={"color": "yellow", "size": 12},
                )
            )
        fig_twitter.add_trace(
            go.Scatter(
                x=[fig_df["last_updated_date"].tolist()[0]], 
                y=[fig_df["twitter_followers_count"].tolist()[0]],
                mode='markers+text',
                marker={"color": "yellow", "size": 12},
                text=[f"{fig_df['twitter_followers_count'].tolist()[0]:,}"],
                textfont={"color": "yellow"},
                textposition="top center"
                )
            )
        fig_twitter.add_trace(
            go.Scatter(
                x=[fig_df["last_updated_date"].tolist()[-1]], 
                y=[fig_df["twitter_followers_count"].tolist()[-1]],
                mode='markers+text',
                marker={"color": "yellow", "size": 12},
                text=[f"{fig_df['twitter_followers_count'].tolist()[-1]:,}"],
                textfont={"color": "yellow"},
                textposition="top center"
                )
            )
        fig_twitter.update_layout(
            xaxis={"showline": True, "showgrid": False, "title": "DATE" },
            yaxis={
                "showgrid": False, 
                "showticklabels": False,
                "range": [
                    min(fig_df["twitter_followers_count"]) * 0.95, 
                    max(fig_df["twitter_followers_count"]) * 1.05
                    ]
                },
            title={"text": "DAILY TOTAL NUMBER OF FOLLOWERS", "x": 0.5},
            showlegend=False
            )

        # General Charts Styles
        for fig_object in [fig_prices, fig_market_caps, fig_total_volumes, fig_github, fig_twitter]:
            fig_object.update_layout(
                xaxis = {
                    "tickformat": "%b %d, %Y",
                    "tickangle": 90,
                    "dtick": 86400000,
                    "range": [
                        min(fig_df["last_updated_date"]) - pd.DateOffset(days=1), 
                        max(fig_df["last_updated_date"]) + pd.DateOffset(days=1)
                        ]
                    },
                plot_bgcolor = "#227B94",
                paper_bgcolor = "#227B94",
                font_color = "white"
                )

        # News Charts Calculations
        temp_news_df = pd.DataFrame(data_objects['news']).dropna()
        temp_news_df = temp_news_df.loc[
            [
                news_id not in self.news_df["id"].to_list() 
                if len(self.news_df) > 0
                else True 
                for news_id in temp_news_df['id']
                ]
            ]
        if len(temp_news_df) > 0:
            temp_news_df["published_date"] = pd.to_datetime(temp_news_df["published_date"], utc=True)
            temp_news_df["subtitle"] = (
                "By "+ temp_news_df["author"] +
                " on " + temp_news_df["published_date"].dt.strftime("%b %d, %Y")
                )
            temp_news_df["content_preview"] = (
                "Title: " + temp_news_df["title"] + 
                " Description: " + temp_news_df["description"]
                )
            sentiment_results = (
                pd.DataFrame(self.sentiment_pipeline(temp_news_df["content_preview"].to_list()))
                .rename(columns={"label": "sentiment_label", "score": "sentiment_score"})
                .replace({"LABEL_0": "NEGATIVE", "LABEL_1": "NEUTRAL", "LABEL_2": "POSITIVE"})
                )
            temp_news_df = pd.concat(
                [temp_news_df.reset_index(drop=True), sentiment_results.reset_index(drop=True)], 
                axis="columns",
                )
            if len(self.news_df) == 0:
                self.news_df = temp_news_df.copy()
            else:
                self.news_df = pd.concat(
                    [self.news_df.reset_index(drop=True), temp_news_df.reset_index(drop=True)], 
                    axis="index", 
                    ignore_index=True
                    )
        
        # News Charts Subsets
        news_today = (
            self.news_df[self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=1))]
            .sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=1))).any()
            else self.news_empty_post
            )
        news_this_week = (
            self.news_df[
                (self.news_df["published_date"] < pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=1))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=7)))
                ].sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if ((self.news_df["published_date"] < pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=1))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=7)))).any()
            else self.news_empty_post
            )
        news_this_month = (
            self.news_df[
                (self.news_df["published_date"] < pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=7))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=30)))
                ].sort_values("sentiment_score", ascending=False).iloc[0].to_dict()
            if ((self.news_df["published_date"] < pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=7))) & 
                (self.news_df["published_date"] >= pd.to_datetime(pd.Timestamp.utcnow().floor('D') - pd.DateOffset(days=30)))).any()
            else self.news_empty_post
            )

        # Dashboard Objects
        dash_objects = {
            "headline": {
                "market_cap": statuses_df['market_cap_rank'][-1],
                "ath_usd": statuses_df['ath_usd'][-1],
                "ath_date": statuses_df['ath_date'][-1],
                "atl_usd": statuses_df['atl_usd'][-1],
                "atl_date": statuses_df['atl_date'][-1],
                "last_updated_timestamp": max(
                    pd.to_datetime(self.news_df["published_timestamp"], utc=True).max(), 
                    pd.to_datetime(statuses_df["last_updated_timestamp"], utc=True).max()
                    )
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

    def get_dash_layout(self):
        dash_layout = html.Div(
            [
                # Header Section
                html.Div(
                    [
                        html.H1(
                            [
                                html.Span("The Daily BTC", style={"fontSize": 48}), 
                                html.Img(src=get_asset_url("bitcoin-icon-small.webp"), className="ps-3 pe-3 pb-2"),
                                ]
                            ),
                        html.P(
                            f"""Last updated on 
                            {self.dash_objects['headline']['last_updated_timestamp'].strftime("%Y-%m-%d at %I:%M %p %Z.")}""", 
                            style={"fontStyle": "italic", "fontSize": "12pt"}
                            )
                        ], 
                    className="row ps-4 pe-4 pt-4 pb-1 text-center"
                    ),
                # Headline Section
                html.Div(
                    [
                        html.P(
                            [
                                html.Span(f"MARKET CAP RANK: #{self.dash_objects['headline']['market_cap']}"),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"""ALL-TIME HIGH PRICE: ${self.dash_objects['headline']['ath_usd']:,} 
                                          ON {self.dash_objects['headline']['ath_date']}"""),
                                html.Span(f"|", className="ps-3 pe-3"),
                                html.Span(f"""ALL-TIME LOW PRICE: ${self.dash_objects['headline']['atl_usd']:,} 
                                          ON {self.dash_objects['headline']['atl_date']}""")
                                ]
                            )
                        ], 
                    className="row ps-4 pe-4 text-center"
                    ),
                # News And Charts Sections
                html.Div(
                    [
                        html.Div( # Economic And Social Charts Sections
                            [
                                html.Div( # Economic Charts Section
                                    [
                                        html.P("ECONOMIC CHARTS"),
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=self.dash_objects["economics"]["prices"], 
                                                        style={"width": "100%"}
                                                        ),
                                                    label='PRICES', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#227B94", 
                                                        "borderTop": "1vh solid white"
                                                        }
                                                    ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=self.dash_objects["economics"]["market_caps"], 
                                                        style={"width": "100%"}
                                                        ),
                                                    label='MARKET CAPS', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#227B94", 
                                                        "borderTop": "1vh solid white"
                                                        }
                                                    ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=self.dash_objects["economics"]["total_volumes"], 
                                                        style={"width": "100%"}
                                                        ),
                                                    label='TOTAL VOLUMES', 
                                                    className="text-white pt-1",
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#227B94", 
                                                        "borderTop": "1vh solid white"
                                                        }
                                                    )
                                                ],
                                            style={"height": "5vh"}
                                            )
                                        ], 
                                    className="col pb-5"
                                    ),
                                html.Div( # Social Charts Section
                                    [
                                        html.P("SOCIAL CHARTS"),
                                        dcc.Tabs(
                                            [
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=self.dash_objects["socials"]["github"], 
                                                        style={"width": "100%"}
                                                        ),
                                                    label='GITHUB', 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#227B94", 
                                                        "borderTop": "1vh solid white"
                                                        },
                                                    ),
                                                dcc.Tab(
                                                    dcc.Graph(
                                                        figure=self.dash_objects["socials"]["twitter"], 
                                                        style={"width": "100%"}
                                                        ),
                                                    label='TWITTER', 
                                                    className="text-white pt-1", 
                                                    style={"backgroundColor": "#16325B"},
                                                    selected_style={
                                                        "backgroundColor": "#227B94", 
                                                        "borderTop": "1vh solid white"
                                                        },
                                                    ),
                                                ], 
                                            style={"height": "5vh"}
                                            )
                                        ], 
                                    className="col pb-5"
                                    )
                                ], 
                            className="col-md-8 pe-4"
                            ),
                        html.Div( # News Section
                            [
                                html.P("MAJOR NEWS"),
                                html.Div( # Today
                                    html.Div(
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
                                                                src=self.dash_objects["news"]["today"]["url_to_image"], 
                                                                className="mx-auto w-100",
                                                                ),
                                                            className="d-flex align-items-center"
                                                            ),
                                                        html.A(
                                                            self.dash_objects["news"]["today"]["title"], 
                                                            href=self.dash_objects["news"]["today"]["url_to_post"],
                                                            target="_blank",
                                                            rel="noopener noreferrer"
                                                            ),
                                                        html.Br(),
                                                        html.Span(
                                                            self.dash_objects["news"]["today"]["subtitle"], 
                                                            style={"fontStyle": "italic"}
                                                            )
                                                        ]
                                                    )
                                                ],
                                            className="col p-2"
                                            ),
                                        className="row border rounded"
                                        ),
                                    className="col pb-5"
                                    ),
                                html.Div( # This Week
                                    html.Div(
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
                                                                src=self.dash_objects["news"]["this_week"]["url_to_image"], 
                                                                className="mx-auto w-100",
                                                                ),
                                                            className="d-flex align-items-center"
                                                            ),
                                                        html.A(
                                                            self.dash_objects["news"]["this_week"]["title"], 
                                                            href=self.dash_objects["news"]["this_week"]["url_to_post"],
                                                            target="_blank",
                                                            rel="noopener noreferrer"
                                                            ),
                                                        html.Br(),
                                                        html.Span(
                                                            self.dash_objects["news"]["this_week"]["subtitle"], 
                                                            style={"fontStyle": "italic"}
                                                            )
                                                        ]
                                                    )
                                                ],
                                            className="col p-2"
                                            ),
                                        className="row border rounded"
                                        ),
                                    className="col pb-5"
                                    ),
                                html.Div(  # This Month
                                    html.Div(
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
                                                                src=self.dash_objects["news"]["this_month"]["url_to_image"], 
                                                                className="mx-auto w-100",
                                                                ),
                                                            className="d-flex align-items-center"
                                                            ),
                                                        html.A(
                                                            self.dash_objects["news"]["this_month"]["title"], 
                                                            href=self.dash_objects["news"]["this_month"]["url_to_post"],
                                                            target="_blank",
                                                            rel="noopener noreferrer"
                                                            ),
                                                        html.Br(),
                                                        html.Span(
                                                            self.dash_objects["news"]["this_month"]["subtitle"], 
                                                            style={"fontStyle": "italic"}
                                                            )
                                                        ]
                                                    )
                                                ],
                                            className="col p-2"
                                            ),
                                        className="row border rounded"
                                        ),
                                    className="col pb-5"
                                    ),
                                ], 
                            className="col-md-4 ps-4"
                            )
                        ], 
                    className="row ps-4 pe-4 pt-4"
                    ),
                html.Div( # Footer Section
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
                                        style={"width": "8vh"}
                                        ), 
                                    href="https://www.linkedin.com/in/tamleauthentic/",
                                    target="_blank",
                                    rel="noopener noreferrer"
                                    ),
                                html.A(
                                    html.Img(
                                        src=get_asset_url("github_icon.png"), 
                                        className="p-2", 
                                        style={"width": "8vh"}
                                        ),
                                    href="https://github.com/moodysquirrelapps",
                                    target="_blank",
                                    rel="noopener noreferrer"
                                    )
                                ]
                            )
                        ], 
                    className="row ps-4 pe-4 pb-4",
                    style={"fontStyle": "italic", "fontSize": "12pt", "textAlign": "right", "justify-content": "right"}
                    ),
                ], 
            className="container-fluid bg-dark text-white"
            )
        return dash_layout

    def update_dash_objects(self, data_objects):
        self.dash_objects = self.get_dash_objects(data_objects)
        return None

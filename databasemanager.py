"""
Purpose: A database manager for The Daily BTC Web Application.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey, select, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional, List
import requests
import datetime as dt

load_dotenv()

class Base(DeclarativeBase):
    pass

class Statuses(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    block_time_in_minutes: Mapped[Optional[int]]
    market_cap_rank: Mapped[Optional[int]]
    price_usd: Mapped[Optional[float]]
    ath_usd: Mapped[Optional[int]]
    ath_date: Mapped[Optional[str]]
    atl_usd: Mapped[Optional[int]]
    atl_date: Mapped[Optional[str]]
    market_cap_usd: Mapped[Optional[int]]
    fully_diluted_valuation_usd: Mapped[Optional[int]]
    total_volume_usd: Mapped[Optional[int]]
    circulating_supply: Mapped[Optional[int]]
    max_supply: Mapped[Optional[int]]
    last_updated_timestamp: Mapped[Optional[str]]
    last_updated_date: Mapped[Optional[str]]
    twitter_followers_count: Mapped[Optional[int]]
    github_total_issues_count: Mapped[Optional[int]]
    github_closed_issues_count: Mapped[Optional[int]]
    github_pull_requests_merged_count: Mapped[Optional[int]]
    github_pull_request_contributors_count: Mapped[Optional[int]]

    news_ids_rel: Mapped[List["News"]] = relationship(back_populates="last_updated_date_rel")

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[Optional[str]]
    author: Mapped[Optional[str]]
    title: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    url_to_post: Mapped[str] = mapped_column(unique=True)
    url_to_image: Mapped[Optional[str]]
    published_timestamp: Mapped[Optional[str]]
    published_date: Mapped[Optional[str]] = mapped_column(ForeignKey("statuses.last_updated_date"))
    
    last_updated_date_rel: Mapped[Statuses] = relationship(back_populates="news_ids_rel")

class DataBaseManager:
    def __init__(self):
        self.crypto_id = "bitcoin"
        self.update_rate_sec = 60 * 60 * 1 # 1-Hour Delays Between API Calls
        self.db_path = os.getenv("DB_PATH")
        self.create()

        # CoinGecko API
        ### General Data Endpoint: https://docs.coingecko.com/v3.0.1/reference/coins-id
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.coingecko_api_endpoint = f"https://api.coingecko.com/api/v3/coins/{self.crypto_id}"

        # News API
        ### Everything Endpoint: https://newsapi.org/docs/endpoints/everything
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.news_api_endpoint = "https://newsapi.org/v2/everything"
        return None

    def create(self):
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        return None

    def read(self):
        with Session(self.engine) as session:
            # STATUSES TABLE
            statuses_rows_list = []
            statuses_query_results = session.execute(
                select(Statuses)
                .execution_options(populate_existing=True)
                ).all()
            for statuses_query_result in statuses_query_results:
                statuses_row = {
                    "id": statuses_query_result[0].id,
                    "block_time_in_minutes": statuses_query_result[0].block_time_in_minutes,
                    "price_usd": statuses_query_result[0].price_usd,
                    "ath_usd": statuses_query_result[0].ath_usd,
                    "ath_date": statuses_query_result[0].ath_date,
                    "atl_usd": statuses_query_result[0].atl_usd,
                    "atl_date": statuses_query_result[0].atl_date,
                    "market_cap_usd": statuses_query_result[0].market_cap_usd,
                    "fully_diluted_valuation_usd": statuses_query_result[0].fully_diluted_valuation_usd,
                    "market_cap_rank": statuses_query_result[0].market_cap_rank,
                    "total_volume_usd": statuses_query_result[0].total_volume_usd,
                    "max_supply": statuses_query_result[0].max_supply,
                    "circulating_supply": statuses_query_result[0].circulating_supply,
                    "last_updated_timestamp": statuses_query_result[0].last_updated_timestamp,
                    "last_updated_date": statuses_query_result[0].last_updated_date,
                    "twitter_followers_count": statuses_query_result[0].twitter_followers_count,
                    "github_total_issues_count": statuses_query_result[0].github_total_issues_count,
                    "github_closed_issues_count": statuses_query_result[0].github_closed_issues_count,
                    "github_pull_requests_merged_count": statuses_query_result[0].github_pull_requests_merged_count,
                    "github_pull_request_contributors_count": statuses_query_result[0].github_pull_request_contributors_count
                    }
                statuses_rows_list.append(statuses_row)

            # NEWS TABLE
            news_rows_list = []
            news_query_results = session.execute(
                select(News)
                .execution_options(populate_existing=True)
                ).all()
            for news_query_result in news_query_results:
                news_row = {
                    "id": news_query_result[0].id,
                    "source_name": news_query_result[0].source_name,
                    "author": news_query_result[0].author,
                    "title": news_query_result[0].title,
                    "description": news_query_result[0].description,
                    "url_to_post": news_query_result[0].url_to_post,
                    "url_to_image": news_query_result[0].url_to_image,
                    "published_timestamp": news_query_result[0].published_timestamp,
                    "published_date": news_query_result[0].published_date
                    }
                news_rows_list.append(news_row)

        # DATA OBJECTS
        data_objects = {
            'statuses': statuses_rows_list,
            'news': news_rows_list
            }
        return data_objects

    def update(self):
        # CoinGecko API
        response_coingecko = requests.get(
            url=self.coingecko_api_endpoint, 
            headers={
                "accept": "application/json", 
                "x-cg-demo-api-key": self.coingecko_api_key
                }
            )
        response_coingecko.raise_for_status()
        coingecko_data = response_coingecko.json()

        new_entry_statuses = {
            "block_time_in_minutes": coingecko_data["block_time_in_minutes"],
            "price_usd": coingecko_data["market_data"]["current_price"]["usd"],
            "ath_usd": coingecko_data["market_data"]["ath"]["usd"],
            "ath_date": coingecko_data["market_data"]["ath_date"]["usd"].split("T")[0],
            "atl_usd": coingecko_data["market_data"]["atl"]["usd"],
            "atl_date": coingecko_data["market_data"]["atl_date"]["usd"].split("T")[0],
            "market_cap_usd": coingecko_data["market_data"]["market_cap"]["usd"],
            "fully_diluted_valuation_usd": coingecko_data["market_data"]["fully_diluted_valuation"]["usd"],
            "market_cap_rank": coingecko_data["market_data"]["market_cap_rank"],
            "total_volume_usd": coingecko_data["market_data"]["total_volume"]["usd"],
            "max_supply": coingecko_data["market_data"]["max_supply"],
            "circulating_supply": coingecko_data["market_data"]["circulating_supply"],
            "last_updated_timestamp": coingecko_data["market_data"]["last_updated"],
            "last_updated_date": coingecko_data["market_data"]["last_updated"].split("T")[0],
            "twitter_followers_count": coingecko_data["community_data"]["twitter_followers"],
            "github_total_issues_count": coingecko_data["developer_data"]["total_issues"],
            "github_closed_issues_count": coingecko_data["developer_data"]["closed_issues"],
            "github_pull_requests_merged_count": coingecko_data["developer_data"]["pull_requests_merged"],
            "github_pull_request_contributors_count": coingecko_data["developer_data"]["pull_request_contributors"]
            }

        with Session(self.engine) as session:
            results = (
                session.execute(
                    select(Statuses)
                    .where(Statuses.last_updated_timestamp == new_entry_statuses["last_updated_timestamp"])
                    ).all()
                )
            if len(results) == 0:
                session.execute(insert(Statuses), new_entry_statuses)
                session.commit()

        # News API
        response_news = requests.get(
            url=self.news_api_endpoint, 
            params={
                "q": self.crypto_id,
                "searchIn": "title,description",
                "language": "en",
                "from": (dt.datetime.now() - dt.timedelta(1)).strftime("%Y-%m-%d") + "T00:00:00",
                "to": dt.datetime.now().strftime("%Y-%m-%d") + "T00:00:00"
                },
            headers={
                "accept": "application/json", 
                "X-Api-Key": self.news_api_key
                }
            )
        response_news.raise_for_status()
        news_data = response_news.json()["articles"]

        with Session(self.engine) as session:
            for news in news_data:
                new_entry_news = {
                    "source_name": news["source"]["name"],
                    "author": news["author"],
                    "title": news["title"],
                    "description": news["description"],
                    "url_to_post": news["url"],
                    "url_to_image": news["urlToImage"],
                    "published_timestamp": news["publishedAt"],
                    "published_date": news["publishedAt"].split("T")[0]
                    }
                results = (
                    session.execute(
                        select(News)
                        .where(News.url_to_post == new_entry_news["url_to_post"])
                        ).all()
                    )
                if len(results) == 0:
                    session.execute(insert(News), new_entry_news)
                    session.commit()
        return None

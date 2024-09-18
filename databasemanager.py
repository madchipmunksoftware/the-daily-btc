"""
Purpose: A manager for the database.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, ForeignKey, select, insert, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional, List
import requests
import pandas as pd

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
    last_updated: Mapped[Optional[str]]
    twitter_followers_count: Mapped[Optional[int]]
    github_total_issues_count: Mapped[Optional[int]]
    github_closed_issues_count: Mapped[Optional[int]]
    github_pull_requests_merged_count: Mapped[Optional[int]]
    github_pull_request_contributors_count: Mapped[Optional[int]]

    news_posts_rel: Mapped[List["News"]] = relationship(back_populates="last_updated_rel")

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    last_updated_id = mapped_column(ForeignKey("statuses.last_updated"))

    last_updated_rel: Mapped[Statuses] = relationship(back_populates="news_posts_rel")

class DataBaseManager:
    def __init__(self):
        self.crypto_id = "bitcoin"
        self.update_rate_sec = 60 * 60 # 1-Hour Delays

        # Database
        self.engine = create_engine("sqlite:///instance/daily-btc.db", echo=True)
        # self.engine = create_engine("sqlite:///:memory:", echo=True)
        Base.metadata.create_all(self.engine)

        # CoinGecko API
        self.coingecko_api_key = os.getenv("COINGECK_API")
        self.coingecko_api_url = f"https://api.coingecko.com/api/v3/coins/{self.crypto_id}"
        # General Data Doc: https://docs.coingecko.com/v3.0.1/reference/coins-id

        # News API
        self.news_api_key = os.getenv("News_API")
        self.news_api_url = "https://api.coingecko.com/api/v3/" + f""
        return None

    def read(self):
        with Session(self.engine) as session:
            rows_list = []
            results = session.execute(select(Statuses)).all()
            for result in results:
                row_entry = {
                    "id": result[0].id,
                    "block_time_in_minutes": result[0].block_time_in_minutes,
                    "price_usd": result[0].price_usd,
                    "ath_usd": result[0].ath_usd,
                    "ath_date": result[0].ath_date,
                    "atl_usd": result[0].atl_usd,
                    "atl_date": result[0].atl_date,
                    "market_cap_usd": result[0].market_cap_usd,
                    "fully_diluted_valuation_usd": result[0].fully_diluted_valuation_usd,
                    "market_cap_rank": result[0].market_cap_rank,
                    "total_volume_usd": result[0].total_volume_usd,
                    "max_supply": result[0].max_supply,
                    "circulating_supply": result[0].circulating_supply,
                    "last_updated": result[0].last_updated,
                    "twitter_followers_count": result[0].twitter_followers_count,
                    "github_total_issues_count": result[0].github_total_issues_count,
                    "github_closed_issues_count": result[0].github_closed_issues_count,
                    "github_pull_requests_merged_count": result[0].github_pull_requests_merged_count,
                    "github_pull_request_contributors_count": result[0].github_pull_request_contributors_count
                }
                rows_list.append(row_entry)
                rows_df = pd.DataFrame(rows_list).sort_values("id")
            return rows_df

    def update(self):
        # CoinGecko API
        response_coingecko = requests.get(url=self.coingecko_api_url, 
                                          headers={
                                              "accept": "application/json",
                                              "x-cg-demo-api-key": self.coingecko_api_key
                                              })
        response_coingecko.raise_for_status()
        coingecko_data = response_coingecko.json()

        new_entry_statuses = {
            "block_time_in_minutes": coingecko_data["block_time_in_minutes"],
            "price_usd": coingecko_data["market_data"]["current_price"]["usd"],
            "ath_usd": coingecko_data["market_data"]["ath"]["usd"],
            "ath_date": coingecko_data["market_data"]["ath_date"]["usd"],
            "atl_usd": coingecko_data["market_data"]["atl"]["usd"],
            "atl_date": coingecko_data["market_data"]["atl_date"]["usd"],
            "market_cap_usd": coingecko_data["market_data"]["market_cap"]["usd"],
            "fully_diluted_valuation_usd": coingecko_data["market_data"]["fully_diluted_valuation"]["usd"],
            "market_cap_rank": coingecko_data["market_data"]["market_cap_rank"],
            "total_volume_usd": coingecko_data["market_data"]["total_volume"]["usd"],
            "max_supply": coingecko_data["market_data"]["max_supply"],
            "circulating_supply": coingecko_data["market_data"]["circulating_supply"],
            "last_updated": coingecko_data["market_data"]["last_updated"],
            "twitter_followers_count": coingecko_data["community_data"]["twitter_followers"],
            "github_total_issues_count": coingecko_data["developer_data"]["total_issues"],
            "github_closed_issues_count": coingecko_data["developer_data"]["closed_issues"],
            "github_pull_requests_merged_count": coingecko_data["developer_data"]["pull_requests_merged"],
            "github_pull_request_contributors_count": coingecko_data["developer_data"]["pull_request_contributors"]
        }

        with Session(self.engine) as session:
            results = session.execute(select(Statuses).where(Statuses.last_updated == new_entry_statuses["last_updated"])).all()
            if len(results) == 0:
                session.execute(insert(Statuses), new_entry_statuses)
                session.commit()

        # # News API
        # response_news = requests.get(url=self.news_api_url, 
        #                              headers={
        #                                  "accept": "application/json",
        #                                  "X-Api-Key": self.news_api_key
        #                                  })
        # response_news.raise_for_status()
        # news_data = response_news.json()
        return None

    def delete(self):
        pass

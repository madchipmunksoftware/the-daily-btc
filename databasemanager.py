"""
Purpose: A manager for the database.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, ForeignKey, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional, List
import requests
import pandas as pd

load_dotenv()

class Base(DeclarativeBase):
    pass

class Prices(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]]
    date = mapped_column(Date)

    news_post: Mapped[List["News"]] = relationship(back_populates="date")

    def __repr__(self) -> str:
        return f"Prices(id={self.id!r}, name={self.name!r}, description={self.description!r}, date={self.date!r})"

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    date_id = mapped_column(ForeignKey("prices.date"))

    date: Mapped[Prices] = relationship(back_populates="news_post")

    def __repr__(self) -> str:
        return f"News(id={self.id!r}, date_id={self.date_id!r})"

class DataBaseManager:
    def __init__(self):
        self.bitcoin_id = "bitcoin"
        self.refresh_rate_sec = 60 * 30

        # Database
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        Base.metadata.create_all(self.engine)
        self.prices_table = Prices()
        self.news_table = News()

        # CoinGecko API
        self.coingecko_api_key = os.getenv("COINGECK_API")
        self.coingecko_api_root_url = "https://api.coingecko.com/api/v3/"
        self.coingecko_api_coins_generaldata_url = self.coingecko_api_root_url + f"coins/{self.bitcoin_id}"
        # General Data Doc: https://docs.coingecko.com/v3.0.1/reference/coins-id
        self.coingecko_api_coins_historicalchartdata_url = self.coingecko_api_root_url + f"coins/{self.bitcoin_id}/market_chart"
        # Historical Chart Data Doc: https://docs.coingecko.com/v3.0.1/reference/coins-id-market-chart

        # News API
        self.news_api_key = os.getenv("News_API")
        self.news_api_root_url = "https://api.coingecko.com/api/v3/"
        return None
    
    def test_create(self):
        with self.engine.connect() as connection:
            connection.execute(text("CREATE TABLE some_table (x int, y int)"))
            connection.execute(text("INSERT INTO some_table (x, y) VALUES (:x, :y)"), 
                               [{"x": 1, "y": 2}, {"x": 3, "y": 4}])
            connection.commit()
        return None
    
    def test_query(self):
        stmt1 = text("UPDATE some_table SET y = :y WHERE x = :x")
        stmt2 = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
        with Session(self.engine) as session:
            session.execute(stmt1, {"x": 1, "y": 6})
            session.commit()
            result = session.execute(stmt2, {"y": 2})
            for row in result:
                print(f"x: {row.x} | y: {row.y}")
        return None

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def refresh():
        return None

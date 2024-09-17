"""
Purpose: A manager for the database element.
"""

import os
from dotenv import load_dotenv
import sqlite3
import pandas as pd

load_dotenv()

class DataBaseManager:
    def __init__(self):
        self.coingecko_api_key = os.getenv("COINGECK_API")
        self.news_api_key = os.getenv("NEWS_API")
        self.refresh_rate_sec = 60 * 15
        return None

    def refresh():
        return None

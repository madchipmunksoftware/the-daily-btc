"""
Purpose: A manager for the dashboard.
"""

from dash import Dash
import pandas as pd

class DashBoardManager:
    def __init__(self, flask_app):
        self.dashboard = Dash(__name__, server=flask_app, url_base_pathname="/")
        return None

    def update(data_objects):
        statuses_df = pd.DataFrame(data_objects['statuses'])
        news_df = pd.DataFrame(data_objects['news'])
        return None

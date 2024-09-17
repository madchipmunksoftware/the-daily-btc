"""
Purpose: A manager for the dashboard element.
"""

from dash import Dash
import pandas as pd

class DashBoardManager:
    def __init__(self, flask_app):
        self.dashboard = Dash(__name__, server=flask_app, url_base_pathname="/")
        return None

    def refresh(database_manager):
        pass

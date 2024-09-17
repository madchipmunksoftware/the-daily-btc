"""
Purpose: HTTP Server for Daily BTC Web App.
"""

from flask import Flask, render_template, url_for, request, redirect
from dash import Dash
import pandas as pd
import requests

flask_app = Flask(__name__)
dash_app = Dash(__name__, server=flask_app, url_base_pathname="/")

@flask_app.route("/")
def get_home_page():
    return redirect(dash_app)

if __name__ == "__main__":
    flask_app.run(debug=True)

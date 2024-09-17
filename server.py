"""
Purpose: HTTP Server for Daily BTC Web App.
"""

from flask import Flask, render_template, url_for, request, redirect, jsonify
import requests
from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

flask_app = Flask(__name__)
data_manager = DataBaseManager()
dash_manager = DashBoardManager(flask_app)

@flask_app.route("/")
def get_home_page():
    return redirect(dash_manager.dashboard)

@flask_app.route("/api/get-all-data")
def get_all_data_api():
    return jsonify(BTC={}), 200

if __name__ == "__main__":
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=data_manager.refresh(), 
                      trigger='interval', 
                      seconds=dash_manager.refresh_rate_sec)
    scheduler.add_job(func=dash_manager.refresh(), 
                      args=[data_manager],
                      trigger='interval', 
                      seconds=1.5 * dash_manager.refresh_rate_sec)
    scheduler.start()
    flask_app.run(debug=True)

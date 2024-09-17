"""
Purpose: HTTP Server for Daily BTC Web App.
"""

from flask import Flask, render_template, url_for, request, redirect, jsonify
from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

flask_app = Flask(__name__)
database_manager = DataBaseManager()
exit()
database_manager.test_create()
database_manager.test_query()

dashboard_manager = DashBoardManager(flask_app)

@flask_app.route("/")
def get_home_page():
    return redirect(dashboard_manager.dashboard)

@flask_app.route("/api/get-all-calculated-metrics")
def get_all_calculated_metrics_api():
    return jsonify(BTC={}), 200

if __name__ == "__main__":
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=database_manager.refresh(), 
                      trigger='interval', 
                      seconds=dashboard_manager.refresh_rate_sec)
    scheduler.add_job(func=dashboard_manager.refresh(), 
                      args=[database_manager],
                      trigger='interval', 
                      seconds=1.5 * dashboard_manager.refresh_rate_sec)
    scheduler.start()
    flask_app.run(debug=True)

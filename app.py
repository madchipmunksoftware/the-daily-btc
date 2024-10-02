"""
Purpose: Implementation for The Daily BTC Web Application.
"""

from flask import Flask, redirect
from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

# Instantiate Application
app = Flask(__name__)

@app.route("/")
def get_home_page():
    return redirect("/home/")

# Instantiate Managers With Latest Data
database_manager = DataBaseManager()
database_manager.update_database()
dashboard_manager = DashBoardManager(app, database_manager.read_database())

# Schedule Background Tasks
def update_database_manager():
    database_manager.update_database()
    return None

def update_dashboard_manager():
    dashboard_manager.update_layout(database_manager.read_database())
    return None

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    func=update_database_manager, 
    trigger='interval',
    seconds=database_manager.update_database_rate_sec
    )
scheduler.add_job(
    func=update_dashboard_manager, 
    trigger='interval',
    seconds=database_manager.update_database_rate_sec + 60 * 10 # 10-Minute Delays For DataBase Updates
    )
scheduler.start()

if __name__ == "__main__":
    # Development Server
    app.run(host="0.0.0.0", port=5000)

"""
Purpose: The Daily BTC Web Application.
"""

from flask import Flask, redirect
from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

# Instantiate App
app = Flask(__name__)

@app.route("/")
def get_home_page():
    return redirect("/home/")

# Instantiate Managers With Latest Data
database_manager = DataBaseManager()
dashboard_manager = DashBoardManager(app)
database_manager.update()
dashboard_manager.update(database_manager.read())

# Schedule Background Tasks
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(
    func=database_manager.update, 
    trigger='interval', 
    seconds=database_manager.update_rate_sec
    )
scheduler.add_job(
    func=dashboard_manager.update, 
    args=[database_manager.read()],
    trigger='interval',
    seconds=database_manager.update_rate_sec + 60 * 10 # 10-Minute Delays For DB To Update
    )
scheduler.start()

if __name__ == "__main__":
    # Run Server
    app.run(host="0.0.0.0", port="5000")

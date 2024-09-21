"""
Purpose: HTTP Server for The Daily BTC Web Application.
"""

from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

if __name__ == "__main__":
    # Instantiate Managers
    database_manager = DataBaseManager()
    dashboard_manager = DashBoardManager(__name__)
    dashboard_manager.update(database_manager.read())

    # Schedule Jobs
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=database_manager.update, 
        trigger='interval', 
        seconds=database_manager.update_rate_sec
        )
    scheduler.add_job(
        func = dashboard_manager.update, 
        args = [database_manager.read()],
        trigger = 'interval',
        seconds = database_manager.update_rate_sec + 60 * 5 # 5-Minute Delays For DB To Update
        )
    scheduler.start()

    # Run Server
    dashboard_manager.dashboard.run_server(debug=True)

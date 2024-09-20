"""
Purpose: HTTP Server for Daily BTC Web App.
"""

from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

database_manager = DataBaseManager()
dashboard_manager = DashBoardManager(__name__)

if __name__ == "__main__":
    # Initial Ingestion
    # database_manager.update()
    dashboard_manager.update(database_manager.read())

    # Subsequent Ingestions
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
        seconds = database_manager.update_rate_sec + 60 * 15 # 15-Minute Delay For DB Update
    )
    scheduler.start()

    # Server
    dashboard_manager.dashboard.run_server(debug=True)

"""
Purpose: Server for The Daily BTC Web Application.
"""

from databasemanager import DataBaseManager
from dashboardmanager import DashBoardManager
from apscheduler.schedulers.background import BackgroundScheduler

if __name__ == "__main__":
    # Instantiate Managers With Latest Data
    database_manager = DataBaseManager()
    dashboard_manager = DashBoardManager(__name__)
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

    # Run Dashboard Server
    dashboard_manager.dashboard.run_server()

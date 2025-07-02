from models.battery_log import BatteryLog
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class BatteryService:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_latest_by_device(self):
        """各デバイスの最新状態を取得"""
        subquery = self.db.session.query(
            BatteryLog.device_name,
            self.db.func.max(BatteryLog.timestamp).label("max_time")
        ).group_by(BatteryLog.device_name).subquery()

        latest_logs = self.db.session.query(BatteryLog).join(
            subquery,
            (BatteryLog.device_name == subquery.c.device_name) &
            (BatteryLog.timestamp == subquery.c.max_time)
        ).all()

        return [
            {
                "device_name": log.device_name,
                "level": log.level,
                "charging": log.charging,
                "timestamp": log.timestamp.isoformat()
            }
            for log in latest_logs
        ]

    def save_battery_log(self, device_data):
        """バッテリーログを保存"""
        log = BatteryLog(
            device_name=device_data["device_name"],
            level=device_data["level"],
            charging=device_data["charging"]
        )
        self.db.session.add(log)
        self.db.session.commit()
        return {"status": "ok"}

    def get_device_history(self, device_name):
        """指定デバイスの履歴を取得"""
        logs = BatteryLog.query.filter_by(device_name=device_name).order_by(BatteryLog.timestamp).all()
        return [
            {
                "level": log.level,
                "charging": log.charging,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
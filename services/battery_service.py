from models.battery_log import BatteryLog
from datetime import datetime, timedelta
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

    def get_sleep_drain_analysis(self, device_name, hours=8):
        """
        スリープ時のバッテリードレインを分析
        Args:
            device_name: デバイス名
            hours: 分析する時間範囲（デフォルト8時間）
        """
        # 過去24時間のログを取得
        since = datetime.utcnow() - timedelta(hours=24)
        logs = BatteryLog.query.filter(
            BatteryLog.device_name == device_name,
            BatteryLog.timestamp >= since
        ).order_by(BatteryLog.timestamp).all()

        if len(logs) < 2:
            return {"error": "データが不足しています"}

        # スリープ期間を推定（充電していない長時間の期間）
        sleep_periods = []
        for i in range(len(logs) - 1):
            current = logs[i]
            next_log = logs[i + 1]
            
            # 時間差を計算
            time_diff = (next_log.timestamp - current.timestamp).total_seconds() / 3600
            
            # 充電していない期間で、一定時間以上の gap がある場合はスリープ期間と推定
            if not current.charging and time_diff >= 1:  # 1時間以上
                drain_rate = (current.level - next_log.level) / time_diff
                sleep_periods.append({
                    'start_time': current.timestamp.isoformat(),
                    'end_time': next_log.timestamp.isoformat(),
                    'start_level': current.level * 100,
                    'end_level': next_log.level * 100,
                    'duration_hours': round(time_diff, 2),
                    'drain_percent': round((current.level - next_log.level) * 100, 2),
                    'drain_rate_per_hour': round(drain_rate * 100, 2)
                })

        # 統計情報を計算
        if sleep_periods:
            drain_rates = [p['drain_rate_per_hour'] for p in sleep_periods]
            avg_drain = sum(drain_rates) / len(drain_rates)
            max_drain = max(drain_rates)
            min_drain = min(drain_rates)
            
            return {
                'device_name': device_name,
                'analysis_period': f"過去{hours}時間",
                'sleep_periods': sleep_periods,
                'statistics': {
                    'average_drain_per_hour': round(avg_drain, 2),
                    'max_drain_per_hour': round(max_drain, 2),
                    'min_drain_per_hour': round(min_drain, 2),
                    'total_periods': len(sleep_periods)
                }
            }
        else:
            return {"error": "スリープ期間を検出できませんでした"}
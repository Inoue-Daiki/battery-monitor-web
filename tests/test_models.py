import pytest
from datetime import datetime
from models.battery_log import BatteryLog, db

class TestBatteryLog:
    def test_battery_log_creation(self, app):
        """BatteryLogモデル作成テスト"""
        with app.app_context():
            log = BatteryLog(
                device_name="test_device",
                level=0.85,
                charging=True
            )
            db.session.add(log)
            db.session.commit()
            
            assert log.id is not None
            assert log.device_name == "test_device"
            assert log.level == 0.85
            assert log.charging == True
            assert isinstance(log.timestamp, datetime)

    def test_battery_log_query(self, app):
        """BatteryLogクエリテスト"""
        with app.app_context():
            log1 = BatteryLog(device_name="device1", level=0.90, charging=True)
            log2 = BatteryLog(device_name="device2", level=0.85, charging=False)
            db.session.add(log1)
            db.session.add(log2)
            db.session.commit()
            
            # デバイス名でフィルタリング
            device1_logs = BatteryLog.query.filter_by(device_name="device1").all()
            assert len(device1_logs) == 1
            assert device1_logs[0].level == 0.90

    def test_battery_log_timestamp_default(self, app):
        """タイムスタンプデフォルト値テスト"""
        with app.app_context():
            log = BatteryLog(device_name="test", level=0.5, charging=False)
            db.session.add(log)
            db.session.commit()
            
            # タイムスタンプが自動設定されているか
            assert log.timestamp is not None
            assert isinstance(log.timestamp, datetime)
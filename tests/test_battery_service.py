import pytest
from datetime import datetime, timedelta
from services.battery_service import BatteryService
from models.battery_log import BatteryLog, db

class TestBatteryService:
    def test_init(self, app):
        """サービス初期化テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
    def test_save_battery_log(self, app):
        """バッテリーログ保存テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            device_data = {
                "device_name": "test_device",
                "level": 0.85,
                "charging": True
            }
            result = service.save_battery_log(device_data)
            assert result['status'] == 'ok'
            
            # データベースに保存されているか確認
            log = BatteryLog.query.filter_by(device_name="test_device").first()
            assert log is not None
            assert log.level == 0.85
    def test_get_latest_by_device_empty(self, app):
        """空のデバイス状態取得テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            result = service.get_latest_by_device()
            assert isinstance(result, list)
    def test_get_latest_by_device_with_data(self, app):
        """データありのデバイス状態取得テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            
            # テストデータを保存
            device_data1 = {"device_name": "device1", "level": 0.90, "charging": True}
            device_data2 = {"device_name": "device1", "level": 0.85, "charging": False}
            device_data3 = {"device_name": "device2", "level": 0.70, "charging": True}
            
            service.save_battery_log(device_data1)
            service.save_battery_log(device_data2)
            service.save_battery_log(device_data3)
            
            result = service.get_latest_by_device()
            assert len(result) == 2
            
            # device1の最新は0.85のはず
            device1_data = next((d for d in result if d['device_name'] == 'device1'), None)
            assert device1_data is not None
    def test_get_device_history_empty(self, app):
        """空の履歴取得テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            result = service.get_device_history("nonexistent_device")
            assert isinstance(result, list)
    def test_get_device_history_with_data(self, app):
        """データありの履歴取得テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            
            # テストデータを保存
            device_data1 = {"device_name": "test_device", "level": 0.90, "charging": True}
            device_data2 = {"device_name": "test_device", "level": 0.85, "charging": False}
            
            service.save_battery_log(device_data1)
            service.save_battery_log(device_data2)
            
            result = service.get_device_history("test_device")
    def test_get_sleep_drain_analysis_insufficient_data(self, app):
        """スリープドレイン分析（データ不足）テスト"""
        with app.app_context():
            BatteryLog.query.delete()
            db.session.commit()
            service = BatteryService(db)
            result = service.get_sleep_drain_analysis("nonexistent_device")
            assert 'error' in result
            assert result['error'] == "データが不足しています"
            service.save_battery_log(device_data2)
            
            result = service.get_device_history("test_device")
            assert len(result) == 2

    def test_get_sleep_drain_analysis_insufficient_data(self, app):
        """スリープドレイン分析（データ不足）テスト"""
        with app.app_context():
            service = BatteryService(db)
            result = service.get_sleep_drain_analysis("nonexistent_device")
            assert 'error' in result
            assert result['error'] == "データが不足しています"
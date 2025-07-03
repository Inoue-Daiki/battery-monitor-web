import pytest
from datetime import datetime, timedelta
from services.battery_service import BatteryService
from models.battery_log import BatteryLog, db

class TestBatteryService:
    def test_init(self, app):
        """サービス初期化テスト"""
        with app.app_context():
            service = BatteryService(db)
            assert service.db == db

    def test_save_battery_log(self, app):
        """バッテリーログ保存テスト"""
        with app.app_context():
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
            assert log.charging == True

    def test_get_latest_by_device(self, app):
        """最新デバイス状態取得テスト"""
        with app.app_context():
            service = BatteryService(db)
            
            # テストデータを作成
            log1 = BatteryLog(device_name="device1", level=0.90, charging=True)
            log2 = BatteryLog(device_name="device1", level=0.85, charging=False)
            log3 = BatteryLog(device_name="device2", level=0.70, charging=True)
            db.session.add(log1)
            db.session.add(log2)
            db.session.add(log3)
            db.session.commit()
            
            result = service.get_latest_by_device()
            assert len(result) == 2
            
            # device1の最新は0.85のはず
            device1_data = next(d for d in result if d['device_name'] == 'device1')
            assert device1_data['level'] == 0.85

    def test_get_device_history(self, app):
        """デバイス履歴取得テスト"""
        with app.app_context():
            service = BatteryService(db)
            
            # テストデータを作成
            log1 = BatteryLog(device_name="test_device", level=0.90, charging=True)
            log2 = BatteryLog(device_name="test_device", level=0.85, charging=False)
            log3 = BatteryLog(device_name="other_device", level=0.70, charging=True)
            db.session.add(log1)
            db.session.add(log2)
            db.session.add(log3)
            db.session.commit()
            
            result = service.get_device_history("test_device")
            assert len(result) == 2
            # 時系列順に並んでいるか確認
            assert result[0]['level'] == 0.90

    def test_get_sleep_drain_analysis_insufficient_data(self, app):
        """スリープドレイン分析（データ不足）テスト"""
        with app.app_context():
            service = BatteryService(db)
            
            # データが1つだけ
            log = BatteryLog(device_name="test_device", level=0.85, charging=False)
            db.session.add(log)
            db.session.commit()
            
            result = service.get_sleep_drain_analysis("test_device")
            assert 'error' in result

    def test_get_sleep_drain_analysis_with_data(self, app):
        """スリープドレイン分析（データあり）テスト"""
        with app.app_context():
            service = BatteryService(db)
            
            # 2時間前と現在のデータを作成
            past_time = datetime.utcnow() - timedelta(hours=2)
            log1 = BatteryLog(device_name="test_device", level=0.90, charging=False, timestamp=past_time)
            log2 = BatteryLog(device_name="test_device", level=0.80, charging=False)
            db.session.add(log1)
            db.session.add(log2)
            db.session.commit()
            
            result = service.get_sleep_drain_analysis("test_device")
            # 時間が短すぎるのでスリープ期間として検出されない
            assert 'error' in result or len(result.get('sleep_periods', [])) == 0
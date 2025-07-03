import pytest
import json
from datetime import datetime
from models.battery_log import BatteryLog, db

class TestApp:
    def test_index(self, client):
        """トップページのテスト"""
        response = client.get('/')
        assert response.status_code == 200

    def test_api_summary_empty(self, client):
        """空のサマリーAPIテスト"""
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_api_post_success(self, client):
        """バッテリーデータ投稿のテスト"""
        payload = {
            "device_name": "test_device",
            "level": 0.85,
            "charging": True
        }
        response = client.post('/api/post', 
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_api_post_invalid_data(self, client):
        """無効なデータでの投稿テスト"""
        payload = {
            "device_name": "test_device",
            "level": "invalid",  # 文字列
            "charging": True
        }
        response = client.post('/api/post', 
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 500

    def test_api_summary_with_data(self, client, app):
        """データありのサマリーAPIテスト"""
        with app.app_context():
            # テストデータを作成
            log = BatteryLog(
                device_name="test_device",
                level=0.85,
                charging=True
            )
            db.session.add(log)
            db.session.commit()
        
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['device_name'] == 'test_device'
        assert data[0]['level'] == 0.85
        assert data[0]['charging'] == True

    def test_api_history(self, client, app):
        """履歴APIテスト"""
        with app.app_context():
            # テストデータを作成
            log1 = BatteryLog(device_name="test_device", level=0.90, charging=True)
            log2 = BatteryLog(device_name="test_device", level=0.85, charging=False)
            db.session.add(log1)
            db.session.add(log2)
            db.session.commit()
        
        response = client.get('/api/history/test_device')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

    def test_api_sleep_drain(self, client, app):
        """スリープドレイン分析APIテスト"""
        with app.app_context():
            # テストデータを作成
            log = BatteryLog(device_name="test_device", level=0.85, charging=False)
            db.session.add(log)
            db.session.commit()
        
        response = client.get('/api/sleep-drain/test_device')
        assert response.status_code == 200
        data = json.loads(response.data)
        # データ不足のためエラーが返される
        assert 'error' in data

    def test_device_detail_page(self, client):
        """デバイス詳細ページのテスト"""
        response = client.get('/device/test_device')
        assert response.status_code == 200
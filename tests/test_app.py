import pytest
import json
from datetime import datetime

class TestApp:

    @pytest.fixture(autouse=True)
    def clear_db(self, app):
        """各テスト前にDBをクリア"""
        with app.app_context():
            from app import db
            db.session.remove()
            meta = db.metadata
            for table in reversed(meta.sorted_tables):
                db.session.execute(table.delete())
            db.session.commit()

    def test_index(self, client):
        """トップページのテスト"""
        response = client.get('/')
        assert response.status_code == 200

    def test_api_summary_empty(self, client):
        """空のサマリーAPIテスト"""
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

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

    def test_api_post_invalid_json(self, client):
        """無効なJSONでの投稿テスト"""
        response = client.post('/api/post', 
                              data='invalid json',
                              content_type='application/json')
        assert response.status_code == 500

    def test_api_post_missing_fields(self, client):
        """必須フィールドが欠けている投稿テスト"""
        payload = {
            "device_name": "test_device",
            # level と charging が欠けている
        }
        response = client.post('/api/post', 
                              data=json.dumps(payload),
                              content_type='application/json')
        assert response.status_code == 500

    def test_api_summary_with_data(self, client):
        """データありのサマリーAPIテスト"""
        # まずデータを投稿
        payload = {
            "device_name": "test_device",
            "level": 0.85,
            "charging": True
        }
        post_response = client.post('/api/post', 
                                   data=json.dumps(payload),
                                   content_type='application/json')
        assert post_response.status_code == 200
        
        # サマリーを取得
        response = client.get('/api/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['device_name'] == 'test_device'
        assert data[0]['level'] == 0.85
        assert data[0]['charging'] == True

    def test_api_history_empty(self, client):
        """空の履歴APIテスト"""
        response = client.get('/api/history/nonexistent_device')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 0

    def test_api_history_with_data(self, client):
        """データありの履歴APIテスト"""
        # テストデータを投稿
        payload1 = {"device_name": "test_device", "level": 0.90, "charging": True}
        payload2 = {"device_name": "test_device", "level": 0.85, "charging": False}
        
        for payload in [payload1, payload2]:
            response = client.post('/api/post', 
                                 data=json.dumps(payload), 
                                 content_type='application/json')
            assert response.status_code == 200
        
        response = client.get('/api/history/test_device')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2

    def test_api_sleep_drain_no_data(self, client):
        """データなしのスリープドレイン分析APIテスト"""
        response = client.get('/api/sleep-drain/nonexistent_device')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'error' in data

    def test_device_detail_page(self, client):
        """デバイス詳細ページのテスト"""
        response = client.get('/device/test_device')
        assert response.status_code == 200

    def test_swagger_ui(self, client):
        """Swagger UIのテスト"""
        response = client.get('/apidocs/')
        assert response.status_code == 200
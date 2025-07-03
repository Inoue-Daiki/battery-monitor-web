import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# テスト対象のモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'clients'))

class TestBatteryPost:
    @patch('subprocess.check_output')
    @patch('platform.system')
    def test_get_battery_info_macos(self, mock_system, mock_subprocess):
        """macOSでのバッテリー情報取得テスト"""
        from battery_post import get_battery_info
        
        mock_system.return_value = 'Darwin'
        mock_subprocess.return_value = b"""Currently drawing from 'Battery Power'
 -InternalBattery-0 (id=1234567) 85%; discharging; 3:45 remaining present: true"""
        
        level, charging = get_battery_info()
        assert level == 0.85
        assert charging == False

    @patch('subprocess.check_output')
    @patch('platform.system')
    def test_get_battery_info_macos_charging(self, mock_system, mock_subprocess):
        """macOSでの充電中バッテリー情報取得テスト"""
        from battery_post import get_battery_info
        
        mock_system.return_value = 'Darwin'
        mock_subprocess.return_value = b"""Currently drawing from 'AC Power'
 -InternalBattery-0 (id=1234567) 85%; charging; 1:30 remaining present: true"""
        
        level, charging = get_battery_info()
        assert level == 0.85
        assert charging == True

    @patch('builtins.open')
    @patch('platform.system')
    def test_get_battery_info_linux(self, mock_system, mock_open):
        """Linuxでのバッテリー情報取得テスト"""
        from battery_post import get_battery_info
        
        mock_system.return_value = 'Linux'
        
        # /sys/class/power_supply/BAT0/capacity を模擬
        capacity_mock = MagicMock()
        capacity_mock.read.return_value = "75"
        
        # /sys/class/power_supply/BAT0/status を模擬
        status_mock = MagicMock()
        status_mock.read.return_value = "Discharging"
        
        mock_open.side_effect = [capacity_mock, status_mock]
        
        level, charging = get_battery_info()
        assert level == 0.75
        assert charging == False

    @patch('subprocess.check_output')
    @patch('platform.system')
    def test_get_battery_info_ioreg(self, mock_system, mock_subprocess):
        """ioregでのバッテリー情報取得テスト"""
        from battery_post import get_battery_info_ioreg
        
        mock_system.return_value = 'Darwin'
        mock_subprocess.return_value = b"""
        {
          "IOGeneralInterest" = "IOCommand is not serializable"
          "IsCharging" = Yes
          "ExternalConnected" = Yes
          "AdapterInfo" = 123
        }
        """
        
        charging = get_battery_info_ioreg()
        assert charging == True

    @patch('requests.post')
    @patch('battery_post.get_battery_info')
    def test_main_execution(self, mock_get_battery, mock_post):
        """メイン実行部分のテスト"""
        # バッテリー情報を模擬
        mock_get_battery.return_value = (0.85, True)
        
        # HTTPレスポンスを模擬
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response
        
        # テストは実行部分を含むため、importで実行される
        # 実際のテストでは、メイン実行部分を関数化することを推奨
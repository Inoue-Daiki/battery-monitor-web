import pytest
import os
from config import Config

class TestConfig:
    def test_config_default_values(self):
        """設定のデフォルト値テスト"""
        config = Config()
        assert config.SECRET_KEY == 'dev-secret-key'
        assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///battery.db'
        assert config.SQLALCHEMY_TRACK_MODIFICATIONS == False
        assert config.LOG_LEVEL == 'INFO'
        assert config.HOST == '0.0.0.0'
        assert config.PORT == 5001
        assert config.DEBUG == False

    def test_config_from_env(self, monkeypatch):
        """環境変数からの設定読み込みテスト"""
        monkeypatch.setenv('SECRET_KEY', 'test-secret')
        monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('PORT', '3000')
        monkeypatch.setenv('FLASK_ENV', 'development')
        
        config = Config()
        assert config.SECRET_KEY == 'test-secret'
        assert config.LOG_LEVEL == 'DEBUG'
        assert config.PORT == 3000
        assert config.DEBUG == True
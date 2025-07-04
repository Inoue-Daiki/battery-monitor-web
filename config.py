import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///battery.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5001)
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = os.environ.get('TESTING') == 'true'

class TestConfig(Config):
    """テスト用設定"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    LOG_LEVEL = 'ERROR'
    WTF_CSRF_ENABLED = False
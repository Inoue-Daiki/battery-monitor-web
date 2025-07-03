import pytest
import tempfile
import os
from app import create_app
from models.battery_log import db

@pytest.fixture
def app():
    """テスト用Flaskアプリケーションを作成"""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """テスト用クライアントを作成"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """テスト用CLIランナーを作成"""
    return app.test_cli_runner()
import pytest
import tempfile
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def app():
    """テスト用Flaskアプリケーションを作成"""
    # テスト用一時データベースファイルを作成
    db_fd, db_path = tempfile.mkstemp()
    
    try:
        # 環境変数を設定（create_appでConfigが読み込まれる前に）
        os.environ['TESTING'] = 'true'
        os.environ['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        
        # アプリケーションを作成
        from app import create_app
        app = create_app()
        
        # テスト用設定を上書き
        app.config.update({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key',
            'LOG_LEVEL': 'ERROR'  # テスト中はログを減らす
        })
        
        with app.app_context():
            from models.battery_log import db
            db.create_all()
            yield app
            
    finally:
        # 環境変数をクリーンアップ
        for key in ['TESTING', 'SQLALCHEMY_DATABASE_URI', 'SECRET_KEY']:
            if key in os.environ:
                del os.environ[key]
        
        # ファイルクリーンアップ
        try:
            os.close(db_fd)
            os.unlink(db_path)
        except (OSError, FileNotFoundError):
            pass  # ファイルが既に削除されている場合は無視

@pytest.fixture
def client(app):
    """テスト用クライアントを作成"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """テスト用CLIランナーを作成"""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """テスト用データベースセッションを作成"""
    from models.battery_log import db
    
    with app.app_context():
        # テスト開始前にテーブルをクリア
        db.drop_all()
        db.create_all()
        
        yield db.session
        
        # テスト終了後にロールバック
        db.session.rollback()
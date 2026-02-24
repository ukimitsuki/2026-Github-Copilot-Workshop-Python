"""
pytest 設定と共有フィクスチャ
"""

import pytest
from app import create_app
from models import db
from repositories import SessionRepository


@pytest.fixture
def app():
    """テスト用 Flask アプリケーション"""
    app = create_app(test_config={"TESTING": True})
    
    with app.app_context():
        # テスト前にDB をリセット
        db.create_all()
        yield app
        # テスト後にDB をクリア
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """テスト用 Flask テストクライアント"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テスト用 CLI ランナー"""
    return app.test_cli_runner()

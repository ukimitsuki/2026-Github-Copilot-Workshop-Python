import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app


@pytest.fixture
def app():
    """Flaskアプリケーションのテストフィクスチャ"""
    flask_app.config['TESTING'] = True
    yield flask_app


@pytest.fixture
def client(app):
    """テストクライアントのフィクスチャ"""
    return app.test_client()

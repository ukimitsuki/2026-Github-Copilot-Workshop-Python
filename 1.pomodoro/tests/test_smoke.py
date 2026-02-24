"""
Smoke Test - 基本動作確認テスト

アプリケーションが起動可能で、最小限の機能が正常に動作することを確認
"""


def test_app_creation():
    """アプリが正常に作成されること"""
    from app import create_app

    app = create_app()
    assert app is not None
    assert app.config["DEBUG"] is True


def test_app_testing_config():
    """テスト設定でアプリが作成されること"""
    from app import create_app

    app = create_app(test_config={"TESTING": True})
    assert app.config["TESTING"] is True


def test_home_endpoint(client):
    """ホームエンドポイントが HTML を返すこと"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data or b"<!DOCTYPE" in response.data
    # タイトルを確認（日本語は decode して確認）
    data = response.data.decode('utf-8')
    assert "ポモドーロタイマー" in data


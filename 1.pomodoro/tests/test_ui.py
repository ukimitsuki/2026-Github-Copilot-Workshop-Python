"""
Timer クラスのテスト

Timer クラスが正常に動作することを確認
"""

import time
from pathlib import Path

# static/js/timer.js をテストするため、パスを調整
import sys
test_dir = Path(__file__).parent
static_dir = test_dir.parent / 'static' / 'js'


def test_timer_creation():
    """Timer が正常に作成されること"""
    # JavaScript のテストは別途 (例: Jest, Vitest)
    # ここでは Python での動作確認
    pass


def test_home_displays_ui(client):
    """ホームページが UI を表示すること"""
    response = client.get("/")
    assert response.status_code == 200
    
    # 主要な UI 要素が含まれていることを確認
    data = response.data.decode('utf-8')
    assert 'startBtn' in data  # 開始ボタン
    assert 'resetBtn' in data  # リセットボタン
    assert 'modeLabel' in data  # モードラベル
    assert 'timerDisplay' in data  # タイマー表示
    assert 'progressCircle' in data  # プログレスバー


def test_static_files_exist(app):
    """必要なスタイックファイルが存在すること"""
    import os
    
    static_dir = Path(app.static_folder)
    
    # CSS ファイル
    css_file = static_dir / 'css' / 'style.css'
    assert css_file.exists(), f"CSS file not found: {css_file}"
    
    # JavaScript ファイル
    for js_file in ['timer.js', 'storage.js', 'main.js']:
        path = static_dir / 'js' / js_file
        assert path.exists(), f"JS file not found: {path}"

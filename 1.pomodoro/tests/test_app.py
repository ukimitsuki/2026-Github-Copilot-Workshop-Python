import pytest
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, load_user_data, save_user_data, calculate_level, check_badges


@pytest.fixture
def client():
    """テスト用のFlaskクライアントを作成"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_data_file(tmp_path):
    """一時データファイルを作成"""
    data_file = tmp_path / "user_data.json"
    return str(data_file)


def test_index_page(client):
    """インデックスページが正常に表示される"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'ポモドーロタイマー'.encode('utf-8') in response.data


def test_calculate_level():
    """レベル計算が正しく行われる"""
    assert calculate_level(0) == 1
    assert calculate_level(25) == 1
    assert calculate_level(100) == 2
    assert calculate_level(400) == 3
    assert calculate_level(900) == 4


def test_check_badges_initial():
    """初回完了バッジが正しく付与される"""
    data = {
        'total_pomodoros': 1,
        'streak_days': 1,
        'badges': [],
        'weekly_stats': {},
        'monthly_stats': {}
    }
    badges = check_badges(data)
    assert '初回完了' in badges


def test_check_badges_streak():
    """連続日数バッジが正しく付与される"""
    data = {
        'total_pomodoros': 10,
        'streak_days': 3,
        'badges': [],
        'weekly_stats': {},
        'monthly_stats': {}
    }
    badges = check_badges(data)
    assert '3日連続' in badges
    
    data['streak_days'] = 7
    badges = check_badges(data)
    assert '7日連続' in badges


def test_check_badges_weekly():
    """週間完了バッジが正しく付与される"""
    from datetime import datetime
    week_key = datetime.now().strftime('%Y-W%U')
    
    data = {
        'total_pomodoros': 10,
        'streak_days': 1,
        'badges': [],
        'weekly_stats': {week_key: 10},
        'monthly_stats': {}
    }
    badges = check_badges(data)
    assert '今週10回完了' in badges


def test_check_badges_50_completion():
    """50回達成バッジが正しく付与される"""
    data = {
        'total_pomodoros': 50,
        'streak_days': 1,
        'badges': [],
        'weekly_stats': {},
        'monthly_stats': {}
    }
    badges = check_badges(data)
    assert '50回達成' in badges


def test_api_stats(client):
    """統計APIが正常に動作する"""
    response = client.get('/api/stats')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'total_pomodoros' in data
    assert 'xp' in data
    assert 'level' in data
    assert 'badges' in data
    assert 'streak_days' in data
    assert 'weekly_data' in data
    assert 'monthly_data' in data


def test_api_settings_get(client):
    """設定取得APIが正常に動作する"""
    response = client.get('/api/settings')
    assert response.status_code == 200
    
    settings = json.loads(response.data)
    assert 'focus_duration' in settings
    assert 'short_break' in settings
    assert 'long_break' in settings
    assert 'theme' in settings
    assert 'sound_start' in settings
    assert 'sound_end' in settings
    assert 'sound_tick' in settings
    assert 'visual_effects' in settings


def test_api_settings_post(client):
    """設定保存APIが正常に動作する"""
    new_settings = {
        'focus_duration': 35,
        'short_break': 10,
        'long_break': 20,
        'theme': 'dark',
        'sound_start': False,
        'sound_end': True,
        'sound_tick': True,
        'visual_effects': False
    }
    
    response = client.post('/api/settings',
                          data=json.dumps(new_settings),
                          content_type='application/json')
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] == True
    
    # 設定が正しく保存されたか確認
    response = client.get('/api/settings')
    settings = json.loads(response.data)
    assert settings['focus_duration'] == 35
    assert settings['theme'] == 'dark'
    
    # テスト後にクリーンアップ
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
    if os.path.exists(settings_file):
        os.remove(settings_file)


def test_api_complete(client):
    """ポモドーロ完了APIが正常に動作する"""
    response = client.post('/api/complete')
    assert response.status_code == 200
    
    result = json.loads(response.data)
    assert result['success'] == True
    assert 'xp' in result
    assert 'level' in result
    assert 'new_badges' in result
    assert 'streak_days' in result
    assert 'total_pomodoros' in result
    
    # XPが増加していることを確認
    assert result['xp'] >= 25
    assert result['total_pomodoros'] >= 1


def test_default_settings_values(client):
    """デフォルト設定値が正しい"""
    response = client.get('/api/settings')
    settings = json.loads(response.data)
    
    assert settings['focus_duration'] == 25
    assert settings['short_break'] == 5
    assert settings['long_break'] == 15
    assert settings['theme'] == 'light'
    assert settings['sound_start'] == True
    assert settings['sound_end'] == True
    assert settings['sound_tick'] == False
    assert settings['visual_effects'] == True

"""
API テスト

セッションの作成と統計の取得をテスト
"""

import json
from datetime import date, datetime, timedelta


def test_create_session(client):
    """セッションの作成"""
    now = int(datetime.utcnow().timestamp())
    
    data = {
        'start_ts': now - 60,
        'end_ts': now,
        'duration_sec': 60,
        'kind': 'work',
    }
    
    response = client.post('/api/session', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    result = response.get_json()
    assert result['kind'] == 'work'
    assert result['duration_sec'] == 60
    assert 'id' in result
    assert 'created_at' in result


def test_create_session_invalid_kind(client):
    """無効な kind でセッション作成を失敗させる"""
    now = int(datetime.utcnow().timestamp())
    
    data = {
        'start_ts': now - 60,
        'end_ts': now,
        'duration_sec': 60,
        'kind': 'invalid',
    }
    
    response = client.post('/api/session',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result


def test_create_session_missing_fields(client):
    """必須フィールドなしでセッション作成を失敗させる"""
    data = {
        'start_ts': 123456,
        # end_ts が不足
    }
    
    response = client.post('/api/session',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400


def test_get_stats_today(client):
    """本日の統計を取得"""
    # セッションを作成
    now = int(datetime.utcnow().timestamp())
    
    for i in range(3):
        data = {
            'start_ts': now - (i + 1) * 60,
            'end_ts': now - i * 60,
            'duration_sec': 60,
            'kind': 'work' if i % 2 == 0 else 'short_break',
        }
        client.post('/api/session',
                   data=json.dumps(data),
                   content_type='application/json')
    
    # 統計を取得
    response = client.get('/api/stats')
    
    assert response.status_code == 200
    result = response.get_json()
    assert result['date'] == date.today().isoformat()
    assert result['total_sessions'] == 3
    assert 'total_work_seconds' in result
    assert 'total_break_seconds' in result


def test_get_stats_specific_date(client):
    """指定日付の統計を取得"""
    response = client.get('/api/stats?date=2026-02-24')
    
    assert response.status_code == 200
    result = response.get_json()
    assert result['date'] == '2026-02-24'


def test_get_stats_invalid_date(client):
    """無効な日付形式で統計取得を失敗させる"""
    response = client.get('/api/stats?date=invalid-date')
    
    assert response.status_code == 400

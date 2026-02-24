"""
セッション API ブループリント

POST /api/session - セッションを作成
GET /api/stats - 日別集計を取得
"""

from flask import Blueprint, request, jsonify
from datetime import date
from services import SessionService

session_bp = Blueprint('session', __name__, url_prefix='/api')


@session_bp.route('/session', methods=['POST'])
def create_session():
    """
    セッションを作成

    Request body:
    {
        "start_ts": 1234567890,     # Unix タイムスタンプ（秒）
        "end_ts": 1234567950,       # Unix タイムスタンプ（秒）
        "duration_sec": 60,         # 実際の経過時間（秒）
        "kind": "work"              # セッション種別
    }

    Response:
    {
        "id": 1,
        "start_ts": 1234567890,
        "end_ts": 1234567950,
        "duration_sec": 60,
        "kind": "work",
        "created_at": "2026-02-24T..."
    }
    """
    data = request.get_json()

    # バリデーション
    required_fields = ['start_ts', 'end_ts', 'duration_sec', 'kind']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        start_ts = int(data['start_ts'])
        end_ts = int(data['end_ts'])
        duration_sec = int(data['duration_sec'])
        kind = str(data['kind'])

        # kind のバリデーション
        valid_kinds = ['work', 'short_break', 'long_break']
        if kind not in valid_kinds:
            return jsonify({'error': f'Invalid kind. Must be one of {valid_kinds}'}), 400

        session = SessionService.create_session(start_ts, end_ts, duration_sec, kind)
        return jsonify(session), 201

    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@session_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    日別集計を取得

    Query parameters:
    - date: 対象日付（YYYY-MM-DD 形式、省略時は今日）

    Response:
    {
        "date": "2026-02-24",
        "total_sessions": 3,
        "total_work_seconds": 4500,      # 75 分
        "total_break_seconds": 600,      # 10 分
        "sessions": [...]
    }
    """
    try:
        date_str = request.args.get('date')
        target_date = None

        if date_str:
            target_date = date.fromisoformat(date_str)

        stats = SessionService.get_daily_stats(target_date)
        return jsonify(stats), 200

    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

# Pomodoro Timer App
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

# データファイルのパス
DATA_FILE = os.path.join(os.path.dirname(__file__), 'user_data.json')

def load_user_data():
    """ユーザーデータをロード"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'total_pomodoros': 0,
        'xp': 0,
        'level': 1,
        'badges': [],
        'streak_days': 0,
        'last_completion_date': None,
        'daily_stats': {},
        'weekly_stats': {},
        'monthly_stats': {}
    }

def save_user_data(data):
    """ユーザーデータを保存"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_level(xp):
    """XPからレベルを計算"""
    return xp // 100 + 1

def check_badges(data):
    """達成バッジをチェック"""
    badges = []
    
    # 3日連続バッジ
    if data['streak_days'] >= 3 and '3日連続' not in data['badges']:
        badges.append('3日連続')
    
    # 7日連続バッジ
    if data['streak_days'] >= 7 and '7日連続' not in data['badges']:
        badges.append('7日連続')
    
    # 今週10回完了バッジ
    today = datetime.now()
    week_key = today.strftime('%Y-W%U')
    if week_key in data['weekly_stats'] and data['weekly_stats'][week_key] >= 10:
        if '今週10回完了' not in data['badges']:
            badges.append('今週10回完了')
    
    # 初回完了バッジ
    if data['total_pomodoros'] == 1 and '初回完了' not in data['badges']:
        badges.append('初回完了')
    
    # 50回達成バッジ
    if data['total_pomodoros'] >= 50 and '50回達成' not in data['badges']:
        badges.append('50回達成')
    
    return badges

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/complete', methods=['POST'])
def complete_pomodoro():
    """ポモドーロ完了時の処理"""
    data = load_user_data()
    
    # 統計情報の更新
    data['total_pomodoros'] += 1
    data['xp'] += 25  # 1ポモドーロで25XP
    data['level'] = calculate_level(data['xp'])
    
    # 日付情報の更新
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    week_key = today.strftime('%Y-W%U')
    month_key = today.strftime('%Y-%m')
    
    # デイリー統計
    if date_str not in data['daily_stats']:
        data['daily_stats'][date_str] = 0
    data['daily_stats'][date_str] += 1
    
    # ウィークリー統計
    if week_key not in data['weekly_stats']:
        data['weekly_stats'][week_key] = 0
    data['weekly_stats'][week_key] += 1
    
    # マンスリー統計
    if month_key not in data['monthly_stats']:
        data['monthly_stats'][month_key] = 0
    data['monthly_stats'][month_key] += 1
    
    # ストリークの更新
    if data['last_completion_date']:
        last_date = datetime.fromisoformat(data['last_completion_date'])
        days_diff = (today.date() - last_date.date()).days
        
        if days_diff == 1:
            # 連続
            data['streak_days'] += 1
        elif days_diff > 1:
            # 途切れた
            data['streak_days'] = 1
    else:
        data['streak_days'] = 1
    
    data['last_completion_date'] = today.isoformat()
    
    # バッジのチェック
    new_badges = check_badges(data)
    data['badges'].extend(new_badges)
    
    save_user_data(data)
    
    return jsonify({
        'success': True,
        'xp': data['xp'],
        'level': data['level'],
        'new_badges': new_badges,
        'streak_days': data['streak_days'],
        'total_pomodoros': data['total_pomodoros']
    })

@app.route('/api/stats')
def get_stats():
    """統計情報を取得"""
    data = load_user_data()
    
    # 週間統計（過去7日間）
    today = datetime.now()
    weekly_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        count = data['daily_stats'].get(date_str, 0)
        weekly_data.append({
            'date': date_str,
            'count': count,
            'day': date.strftime('%a')
        })
    
    # 月間統計（過去30日間）
    monthly_data = []
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        count = data['daily_stats'].get(date_str, 0)
        monthly_data.append({
            'date': date_str,
            'count': count
        })
    
    return jsonify({
        'total_pomodoros': data['total_pomodoros'],
        'xp': data['xp'],
        'level': data['level'],
        'badges': data['badges'],
        'streak_days': data['streak_days'],
        'weekly_data': weekly_data,
        'monthly_data': monthly_data
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """設定の取得・保存"""
    settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
    
    if request.method == 'POST':
        settings_data = request.json
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True})
    else:
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                return jsonify(json.load(f))
        # デフォルト設定
        return jsonify({
            'focus_duration': 25,
            'short_break': 5,
            'long_break': 15,
            'theme': 'light',
            'sound_start': True,
            'sound_end': True,
            'sound_tick': False,
            'visual_effects': True
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

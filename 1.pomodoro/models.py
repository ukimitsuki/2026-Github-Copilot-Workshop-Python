"""
データベースモデル

SQLAlchemy を使用してセッション情報を定義
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Session(db.Model):
    """セッションモデル"""
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    start_ts = db.Column(db.Integer, nullable=False)  # Unix タイムスタンプ（秒）
    end_ts = db.Column(db.Integer, nullable=False)  # Unix タイムスタンプ（秒）
    duration_sec = db.Column(db.Integer, nullable=False)  # 実際の経過時間（秒）
    kind = db.Column(db.String(50), nullable=False)  # 'work' | 'short_break' | 'long_break'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Session(id={self.id}, kind={self.kind}, duration={self.duration_sec}s)>"

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'id': self.id,
            'start_ts': self.start_ts,
            'end_ts': self.end_ts,
            'duration_sec': self.duration_sec,
            'kind': self.kind,
            'created_at': self.created_at.isoformat(),
        }

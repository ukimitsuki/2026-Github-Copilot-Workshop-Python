"""
リポジトリレイヤー

データベース操作を抽象化し、ビジネスロジックから分離
"""

from datetime import datetime, date
from models import db, Session


class SessionRepository:
    """セッションのリポジトリクラス"""

    @staticmethod
    def add_session(start_ts: int, end_ts: int, duration_sec: int, kind: str) -> Session:
        """
        新しいセッションを追加

        Args:
            start_ts: セッション開始時刻（Unix タイムスタンプ・秒）
            end_ts: セッション終了時刻（Unix タイムスタンプ・秒）
            duration_sec: 実際の経過時間（秒）
            kind: セッション種別 ('work' | 'short_break' | 'long_break')

        Returns:
            Session: 作成されたセッション
        """
        session = Session(
            start_ts=start_ts,
            end_ts=end_ts,
            duration_sec=duration_sec,
            kind=kind,
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_sessions_by_date(target_date: date = None) -> list:
        """
        指定日付のセッション一覧を取得

        Args:
            target_date: 対象日付（None の場合は今日）

        Returns:
            list: Session オブジェクトのリスト
        """
        if target_date is None:
            target_date = date.today()

        # Unix タイムスタンプで日付を判定
        # 日の開始（00:00:00 UTC）と終了（23:59:59 UTC）
        day_start = datetime(target_date.year, target_date.month, target_date.day)
        day_end = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

        start_ts = int(day_start.timestamp())
        end_ts = int(day_end.timestamp())

        sessions = Session.query.filter(
            Session.start_ts >= start_ts,
            Session.start_ts <= end_ts,
        ).order_by(Session.created_at.asc()).all()

        return sessions

    @staticmethod
    def get_all_sessions() -> list:
        """すべてのセッションを取得"""
        return Session.query.order_by(Session.created_at.asc()).all()

    @staticmethod
    def delete_session(session_id: int) -> bool:
        """セッションを削除"""
        session = Session.query.get(session_id)
        if not session:
            return False
        db.session.delete(session)
        db.session.commit()
        return True

    @staticmethod
    def clear_all() -> None:
        """すべてのセッションをクリア（テスト用）"""
        Session.query.delete()
        db.session.commit()

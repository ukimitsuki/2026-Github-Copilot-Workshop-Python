"""
サービスレイヤー

ビジネスロジックを実装
"""

from datetime import date
from repositories import SessionRepository


class SessionService:
    """セッション関連のビジネスロジック"""

    @staticmethod
    def create_session(start_ts: int, end_ts: int, duration_sec: int, kind: str):
        """
        セッションを作成

        Args:
            start_ts: セッション開始時刻（Unix タイムスタンプ・秒）
            end_ts: セッション終了時刻（Unix タイムスタンプ・秒）
            duration_sec: 実際の経過時間（秒）
            kind: セッション種別

        Returns:
            dict: セッション情報
        """
        session = SessionRepository.add_session(start_ts, end_ts, duration_sec, kind)
        return session.to_dict()

    @staticmethod
    def get_daily_stats(target_date: date = None) -> dict:
        """
        指定日付の集計情報を取得

        Args:
            target_date: 対象日付（None の場合は今日）

        Returns:
            dict: 集計情報 {
                'date': 'YYYY-MM-DD',
                'total_sessions': 完了セッション数,
                'total_work_seconds': 作業時間合計（秒）,
                'total_break_seconds': 休憩時間合計（秒）,
                'sessions': セッション情報リスト
            }
        """
        if target_date is None:
            target_date = date.today()

        sessions = SessionRepository.get_sessions_by_date(target_date)

        total_work_seconds = 0
        total_break_seconds = 0

        for session in sessions:
            if session.kind == 'work':
                total_work_seconds += session.duration_sec
            else:
                total_break_seconds += session.duration_sec

        return {
            'date': target_date.isoformat(),
            'total_sessions': len(sessions),
            'total_work_seconds': total_work_seconds,
            'total_break_seconds': total_break_seconds,
            'sessions': [s.to_dict() for s in sessions],
        }

    @staticmethod
    def get_work_sessions_today(target_date: date = None) -> int:
        """本日の作業セッション数を取得"""
        stats = SessionService.get_daily_stats(target_date)
        work_sessions = [s for s in stats['sessions'] if s['kind'] == 'work']
        return len(work_sessions)

    @staticmethod
    def get_total_work_seconds_today(target_date: date = None) -> int:
        """本日の合計作業時間（秒）を取得"""
        stats = SessionService.get_daily_stats(target_date)
        return stats['total_work_seconds']

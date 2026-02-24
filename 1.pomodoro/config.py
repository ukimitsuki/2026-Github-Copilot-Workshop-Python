"""
ポモドーロタイマー設定モジュール

Development / Testingの設定を定義
"""


class Config:
    """基本設定"""
    SECRET_KEY = "dev-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """開発環境用設定"""
    DEBUG = True
    TESTING = False
    # SQLite（ファイルベース）
    SQLALCHEMY_DATABASE_URI = "sqlite:///pomodoro.db"


class TestingConfig(Config):
    """テスト環境用設定"""
    DEBUG = True
    TESTING = True
    # SQLite（メモリ）
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

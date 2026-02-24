"""
ポモドーロタイマー Web アプリケーション

Flask アプリケーションの初期化と各種設定
"""

"""
ポモドーロタイマー Web アプリケーション

Flask アプリケーションの初期化と各種設定
"""

from flask import Flask, render_template
from config import DevelopmentConfig, TestingConfig
from models import db
from api.session import session_bp


def create_app(test_config=None):
    """
    Flask アプリケーションファクトリ

    Args:
        test_config (dict, optional): テスト用設定字引。
            テスト時に本設定を上書きする。

    Returns:
        Flask: 初期化された Flask アプリケーション

    Example:
        # 通常モード（開発環境）
        app = create_app()

        # テストモード
        app = create_app(test_config={'TESTING': True, ...})
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # 設定の読み込み
    if test_config is None:
        # 開発環境用設定を使用
        app.config.from_object(DevelopmentConfig)
    else:
        # テスト設定を使用
        app.config.from_object(TestingConfig)
        # テスト設定を上書き
        app.config.update(test_config)

    # DB 初期化
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ブループリント登録
    app.register_blueprint(session_bp)

    @app.route("/")
    def index():
        """ホームページを返す（HTML UI）"""
        return render_template('index.html')

    return app


    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

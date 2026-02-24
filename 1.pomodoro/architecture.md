# ポモドーロタイマー — アーキテクチャ案

## 概要
本プロジェクトは Flask をバックエンドに、HTML/CSS/JavaScript をフロントエンドに用いたシンプルなポモドーロタイマー Web アプリを作成します。クライアント側でタイマー表示を行い、完了したセッションのみサーバに保存して日次集計を行います。

## 目的と重点
- クライアントで滑らかかつ正確なタイマー表示
- 完了セッションの保存と日別集計（今日の進捗表示）
- ユニットテストが書きやすい設計

## 推奨フォルダ構成
- `1.pomodoro/`
  - `app.py`（`create_app` を提供する Flask エントリ）
  - `config.py`（Development / Testing 設定）
  - `models.py`（DB モデル）
  - `repositories.py`（DB 操作を抽象化）
  - `services.py`（ビジネスロジック）
  - `api/`（Blueprint による API 実装）
  - `templates/`（`index.html` 等）
  - `static/`（`css/`, `js/`）
- `requirements.txt`
- `tests/`（pytest 用フィクスチャ・テスト）

## 主要コンポーネント

- Flask アプリ
  - `GET /` → UI（`index.html`）
  - `POST /api/session` → 完了セッションの登録（JSON）
  - `GET /api/stats?date=YYYY-MM-DD` → 日別集計を JSON で返す

- フロントエンド
  - `static/js/timer.js`: `Timer` クラスとして実装し、`now()` を注入可能にする
  - UI: 円形プログレス、開始/リセットボタン、今日の進捗カード
  - localStorage で途中状態を保存して再読み込み復帰

- DB
  - SQLite（小規模）を想定。将来 PostgreSQL に切替可能。
  - `sessions` テーブル: id, start_ts, end_ts, duration_sec, kind, created_at

## テストしやすさのための設計（必須改善点）
- `create_app(test_config=None)` を導入し、テスト時に別設定（SQLite in-memory 等）を注入できるようにする。
- `config.py` に `TestingConfig` を用意する。
- API と UI を `Blueprint` で分離する（個別テストが容易）。
- DB 操作を `SessionRepository` のようなクラスに抽象化し、モック可能にする。
- ビジネスロジックは `services.py` に切り出す（純粋関数に近づける）。
- 時刻取得を注入可能にして時間依存処理を固定化（`freezegun` や注入で対応）。
- フロントの副作用（`localStorage`）はラッパーで抽象化し、テスト時に置換する。

## 技術選定・理由
- Flask: 軽量で学習コストが低く、API とテンプレート両方を簡単に実装できる。
- SQLite: 小規模データの保存に十分でセットアップ不要。テストは in-memory を使用。
- Vanilla JS / ES Modules: 依存を減らし、`Timer` の単体テストを容易にする。

## 開発フロー（短期優先順）
1. `create_app` と `config.py` を作成し、`TestingConfig` を用意する。
2. 最小の `index.html` と `static/js/timer.js`（Timer クラス）を実装してブラウザで動く状態にする。
3. `models.py` / `repositories.py` / `services.py` を追加し、`POST /api/session` と `GET /api/stats` を実装する。
4. `tests/` に pytest フィクスチャと基本的な API テスト、サービスのユニットテストを追加する。
5. UI のスタイルをモックに合わせて整え、E2E テスト（Playwright 等）を必要に応じて追加する。

## 実行（想定コマンド）
開発時の簡易実行例:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=1.pomodoro.app:create_app
flask run
```

（テスト）
```bash
pip install -r requirements-dev.txt
pytest
```

## 次のアクション候補
- 最短スキャフォールド（`create_app` + `index.html` + `timer.js`）を作成して動作確認する
- 完全スキャフォールド（`repositories`/`services`/`tests` を含む）を作成する

---
このファイルは初期設計の要約です。必要ならば項目ごとに具体的なコードスニペットや API スキーマを追加します。

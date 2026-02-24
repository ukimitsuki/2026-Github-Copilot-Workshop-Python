# ポモドーロタイマー — 段階的実装計画

このファイルは添付のアーキテクチャ案・機能一覧・画面イメージを踏まえ、段階的に実装するための計画（ステージ分け・粒度・優先度・スプリント目安）を示します。各ステージはさらに小さなコミット単位に分解して進めてください。

## 概要（優先度）
- 最優先: Stage 0 → Stage 1 → Stage 2（MVP を早期に動作させる）
- 中期: Stage 3（ユーザー設定・通知・サイクル管理）
- 後期: Stage 4〜5（テスト整備・CI・公開準備・アクセシビリティ）

---

## Stage 0 — Developer Setup（前準備）
- 目的: すぐに起動・テストできる開発基盤を作る
- 主要タスク（小コミット単位）:
  1. `requirements.txt`（必要最小限の依存）を追加
  2. `1.pomodoro/create_app` 骨子を `1.pomodoro/app.py` に作成
  3. `config.py` に `DevelopmentConfig`/`TestingConfig` を追加
  4. ディレクトリ構成作成: `templates/`, `static/js/`, `static/css/`, `api/`, `tests/`
  5. `pytest` 初期設定と簡単な smoke test を追加
- 目安: 1〜2 日（1〜3 コミット）

## Stage 1 — MVP: UI とタイマーコア
- 目的: ユーザーが基本操作できる実動作を早く確認する
- 主要タスク:
  1. `templates/index.html`（最小 UI）を作成
  2. `static/js/timer.js` に `Timer` クラス実装（`start`, `pause`, `reset`, `tick`、`now()` 注入可能）
  3. `static/js/main.js` で UI と Timer を結合
  4. localStorage による途中状態保存と復帰
  5. ボタンのアクセシビリティ基本（aria、キーボードショートカット）
- 目安: 2〜5 日（4〜6 コミット）

## Stage 2 — 永続化と API
- 目的: 完了セッションを保存して日次集計を表示する
- 主要タスク:
  1. `models.py` に `sessions` テーブル定義（SQLite）
  2. `repositories.py` に `SessionRepository` 実装
  3. API ブループリント: `POST /api/session`, `GET /api/stats` を実装
  4. クライアントで完了時に POST、失敗時はローカルキューに格納して再送ロジック
  5. UI に「今日の進捗カード」を追加（`GET /api/stats` を利用）
- 目安: 3〜7 日（5〜8 コミット）

## Stage 3 — サイクル管理・設定・通知
- 目的: 実用的なポモドーロ運用に必要な機能を追加
- 主要タスク:
  1. サイクル遷移ロジック（作業→短休→長休、長休の間隔）
  2. 設定 UI（時間／サウンド／通知／自動開始／テーマ）
  3. Web Notifications とサウンド実装（許可取得・ミュート対応）
  4. スキップ、Auto-start、設定反映の実装
  5. UI の視覚的改善（円形プログレスの滑らかな描画）
- 目安: 5〜10 日（6〜10 コミット）

## Stage 4 — テスト・信頼性・CI
- 目的: 品質と保守性を高める
- 主要タスク:
  1. `services.py`（ビジネスロジック）単体テスト
  2. `repositories.py` と DB 操作のテスト（in-memory SQLite）
  3. `static/js/timer.js` のユニットテスト（`now()` をモック）
  4. API の統合テスト（pytest + test client）
  5. GitHub Actions での CI ワークフロー追加（テスト実行）
- 目安: 3〜7 日（テスト追加は継続的）

## Stage 5 — 仕上げ・アクセシビリティ・デプロイ
- 目的: 公開運用に耐える品質とドキュメント整備
- 主要タスク:
  1. アクセシビリティ強化（ARIA, キーボード, コントラスト調整）
  2. マルチタブ制御・時刻ズレ補正・信頼性改善
  3. ロギング・エラーモニタリング導入（任意）
  4. Dockerfile 作成とデプロイ手順、README 更新
  5. パフォーマンス確認と微調整
- 目安: 3〜10 日（運用準備により増減）

---

## スプリントとコミット粒度の推奨
- スプリント長: 1 〜 2 週間
- 1 コミットは「小さく意味のある変更」にする（例: UI マークアップ追加 / Timer API 実装 / localStorage の保存ロジック）
- 各ステージをさらに 3〜8 の小タスクに分解して PR 単位で進めるとレビューしやすい

## 優先で作るべき小タスクの例（今すぐ取り掛かる）
1. `1.pomodoro/app.py` に `create_app` の骨子を追加
2. `templates/index.html`（最小 UI）を追加
3. `static/js/timer.js` に `Timer` クラスのスケルトンを追加
4. `static/js/main.js` で UI と Timer を接続し、開始/停止/リセット が動くことを確認
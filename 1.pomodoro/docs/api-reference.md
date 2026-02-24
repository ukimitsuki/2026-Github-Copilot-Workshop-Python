# API リファレンス

このドキュメントは、ポモドーロタイマーアプリケーションの REST API エンドポイントの詳細を記載しています。

## 目次

- [エンドポイント一覧](#エンドポイント一覧)
- [詳細仕様](#詳細仕様)

## エンドポイント一覧

| メソッド | エンドポイント | 説明 |
|---------|--------------|------|
| GET | `/` | メインページを表示 |
| POST | `/api/complete` | ポモドーロ完了時の処理 |
| GET | `/api/stats` | 統計情報を取得 |
| GET | `/api/settings` | 設定情報を取得 |
| POST | `/api/settings` | 設定情報を保存 |

## 詳細仕様

### GET `/`

メインページ（index.html）を表示します。

**レスポンス**
- `200 OK`: HTMLページ

---

### POST `/api/complete`

ポモドーロを完了した際に呼び出されます。統計情報、XP、レベル、バッジ、ストリークを更新します。

**リクエスト**
- Content-Type: 不要（リクエストボディなし）

**レスポンス**
- `200 OK`

````json
{
  "success": true,
  "xp": 125,
  "level": 2,
  "new_badges": ["初回完了"],
  "streak_days": 3,
  "total_pomodoros": 5
}
````

**フィールド説明**

| フィールド | 型 | 説明 |
|----------|---|------|
| `success` | boolean | 処理が成功したかどうか |
| `xp` | integer | 累積経験値（1ポモドーロ = 25 XP） |
| `level` | integer | 現在のレベル（XP ÷ 100 + 1） |
| `new_badges` | array[string] | 新しく獲得したバッジのリスト |
| `streak_days` | integer | 連続日数 |
| `total_pomodoros` | integer | 累積完了ポモドーロ数 |

**ビジネスロジック**

1. **統計更新**
   - `total_pomodoros` を 1 増加
   - `xp` を 25 増加
   - `level` を再計算（XP ÷ 100 + 1）

2. **日別統計の記録**
   - `daily_stats`: 日付ごとの完了数
   - `weekly_stats`: 週ごとの完了数
   - `monthly_stats`: 月ごとの完了数

3. **ストリーク計算**
   - 前回完了日から1日経過: `streak_days` を 1 増加
   - 前回完了日から2日以上経過: `streak_days` を 1 にリセット
   - 同日: `streak_days` を変更しない

4. **バッジチェック**
   - 初回完了: `total_pomodoros == 1`
   - 3日連続: `streak_days >= 3`
   - 7日連続: `streak_days >= 7`
   - 今週10回完了: 今週の `weekly_stats >= 10`
   - 50回達成: `total_pomodoros >= 50`

---

### GET `/api/stats`

統計情報を取得します。週間・月間のグラフ表示用データを含みます。

**レスポンス**
- `200 OK`

````json
{
  "total_pomodoros": 15,
  "xp": 375,
  "level": 4,
  "badges": ["初回完了", "3日連続"],
  "streak_days": 5,
  "weekly_data": [
    {
      "date": "2026-02-18",
      "count": 3,
      "day": "Tue"
    },
    {
      "date": "2026-02-19",
      "count": 2,
      "day": "Wed"
    }
  ],
  "monthly_data": [
    {
      "date": "2026-02-01",
      "count": 1
    },
    {
      "date": "2026-02-02",
      "count": 0
    }
  ]
}
````

**フィールド説明**

| フィールド | 型 | 説明 |
|----------|---|------|
| `total_pomodoros` | integer | 累積完了ポモドーロ数 |
| `xp` | integer | 累積経験値 |
| `level` | integer | 現在のレベル |
| `badges` | array[string] | 獲得済みバッジのリスト |
| `streak_days` | integer | 連続日数 |
| `weekly_data` | array[object] | 過去7日間の日別データ |
| `monthly_data` | array[object] | 過去30日間の日別データ |

**weekly_data / monthly_data のオブジェクト構造**

| フィールド | 型 | 説明 |
|----------|---|------|
| `date` | string | 日付（YYYY-MM-DD形式） |
| `count` | integer | その日の完了ポモドーロ数 |
| `day` | string | 曜日の略称（weekly_dataのみ） |

---

### GET `/api/settings`

ユーザーの設定情報を取得します。設定ファイルが存在しない場合はデフォルト値を返します。

**レスポンス**
- `200 OK`

````json
{
  "focus_duration": 25,
  "short_break": 5,
  "long_break": 15,
  "theme": "light",
  "sound_start": true,
  "sound_end": true,
  "sound_tick": false,
  "visual_effects": true
}
````

**フィールド説明**

| フィールド | 型 | デフォルト値 | 説明 |
|----------|---|-----------|------|
| `focus_duration` | integer | 25 | 集中時間（分） |
| `short_break` | integer | 5 | 短い休憩時間（分） |
| `long_break` | integer | 15 | 長い休憩時間（分） |
| `theme` | string | "light" | テーマ（"light", "dark", "focus"） |
| `sound_start` | boolean | true | 開始音を有効にするか |
| `sound_end` | boolean | true | 終了音を有効にするか |
| `sound_tick` | boolean | false | Tick音を有効にするか |
| `visual_effects` | boolean | true | 背景エフェクトを有効にするか |

**focus_duration の選択肢**
- 15分
- 25分（デフォルト）
- 35分
- 45分

**short_break の選択肢**
- 5分（デフォルト）
- 10分
- 15分

**long_break の選択肢**
- 15分（デフォルト）
- 20分
- 30分

---

### POST `/api/settings`

ユーザーの設定情報を保存します。

**リクエスト**
- Content-Type: `application/json`

````json
{
  "focus_duration": 35,
  "short_break": 10,
  "long_break": 20,
  "theme": "dark",
  "sound_start": false,
  "sound_end": true,
  "sound_tick": true,
  "visual_effects": false
}
````

**レスポンス**
- `200 OK`

````json
{
  "success": true
}
````

**フィールド説明**

| フィールド | 型 | 説明 |
|----------|---|------|
| `success` | boolean | 設定の保存に成功したかどうか |

---

## データ永続化

アプリケーションは以下のJSONファイルにデータを保存します。

### user_data.json

ユーザーの統計情報とゲーミフィケーションデータを保存します。

````json
{
  "total_pomodoros": 15,
  "xp": 375,
  "level": 4,
  "badges": ["初回完了", "3日連続"],
  "streak_days": 5,
  "last_completion_date": "2026-02-24T12:34:56.789012",
  "daily_stats": {
    "2026-02-24": 3,
    "2026-02-23": 5
  },
  "weekly_stats": {
    "2026-W08": 12
  },
  "monthly_stats": {
    "2026-02": 15
  }
}
````

### settings.json

ユーザーの設定情報を保存します。

````json
{
  "focus_duration": 25,
  "short_break": 5,
  "long_break": 15,
  "theme": "light",
  "sound_start": true,
  "sound_end": true,
  "sound_tick": false,
  "visual_effects": true
}
````

## エラーハンドリング

現在のAPIはエラーレスポンスを明示的に定義していません。すべてのエンドポイントが正常系の `200 OK` を返す設計になっています。

ファイルI/Oエラーやその他の例外はFlaskのデフォルトエラーハンドラーによって処理されます。

## セキュリティ考慮事項

- 認証・認可機能は実装されていません
- データは全てローカルのJSONファイルに保存されます
- CORS設定が有効な場合、クロスオリジンリクエストが許可される可能性があります
- プロダクション環境では `FLASK_ENV=development` を設定しないでください

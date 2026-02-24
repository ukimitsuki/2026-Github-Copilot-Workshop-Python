# データモデル仕様

このドキュメントは、ポモドーロタイマーアプリケーションで使用されるデータモデルの詳細を記載しています。

## 目次

- [概要](#概要)
- [ユーザーデータモデル](#ユーザーデータモデル)
- [設定データモデル](#設定データモデル)
- [APIレスポンスモデル](#apiレスポンスモデル)

## 概要

アプリケーションは以下の2つのJSONファイルにデータを永続化します。

- `user_data.json`: ユーザーの統計情報、XP、レベル、バッジ、ストリーク
- `settings.json`: ユーザーのカスタム設定

## ユーザーデータモデル

### UserData

ユーザーの統計情報とゲーミフィケーションデータを保持します。

**ファイル**: `user_data.json`

**構造**

````json
{
  "total_pomodoros": 15,
  "xp": 375,
  "level": 4,
  "badges": ["初回完了", "3日連続", "7日連続"],
  "streak_days": 7,
  "last_completion_date": "2026-02-24T12:34:56.789012",
  "daily_stats": {
    "2026-02-24": 3,
    "2026-02-23": 5,
    "2026-02-22": 4
  },
  "weekly_stats": {
    "2026-W08": 12,
    "2026-W07": 8
  },
  "monthly_stats": {
    "2026-02": 15,
    "2026-01": 25
  }
}
````

**フィールド定義**

| フィールド | 型 | 必須 | デフォルト値 | 説明 |
|----------|---|------|-----------|------|
| `total_pomodoros` | integer | ✓ | 0 | 累積完了ポモドーロ数 |
| `xp` | integer | ✓ | 0 | 累積経験値（1ポモドーロ = 25 XP） |
| `level` | integer | ✓ | 1 | 現在のレベル |
| `badges` | array[string] | ✓ | [] | 獲得済みバッジのリスト |
| `streak_days` | integer | ✓ | 0 | 連続完了日数 |
| `last_completion_date` | string (ISO 8601) | ✓ | null | 最後の完了日時 |
| `daily_stats` | object | ✓ | {} | 日別完了数の辞書 |
| `weekly_stats` | object | ✓ | {} | 週別完了数の辞書 |
| `monthly_stats` | object | ✓ | {} | 月別完了数の辞書 |

### フィールド詳細

#### total_pomodoros

累積完了ポモドーロ数。ポモドーロを1つ完了するごとに1増加します。

- 型: `integer`
- 最小値: 0
- 更新タイミング: POST `/api/complete` 時

#### xp

累積経験値。ポモドーロを1つ完了するごとに25増加します。

- 型: `integer`
- 最小値: 0
- 増加量: 25 / ポモドーロ
- 更新タイミング: POST `/api/complete` 時

#### level

現在のレベル。XPから自動計算されます。

- 型: `integer`
- 最小値: 1
- 計算式: `level = xp // 100 + 1`
- 更新タイミング: POST `/api/complete` 時

**レベルとXPの対応表**

| レベル | 必要XP | 必要ポモドーロ数 |
|-------|-------|---------------|
| 1 | 0-99 | 0-3 |
| 2 | 100-199 | 4-7 |
| 3 | 200-299 | 8-11 |
| 4 | 300-399 | 12-15 |
| 5 | 400-499 | 16-19 |

#### badges

獲得済みバッジのリスト。重複なしで保存されます。

- 型: `array[string]`
- デフォルト: `[]`
- 更新タイミング: POST `/api/complete` 時

**利用可能なバッジ**

| バッジ名 | 獲得条件 | 実装関数 |
|---------|---------|---------|
| 初回完了 | `total_pomodoros == 1` | `check_badges()` |
| 3日連続 | `streak_days >= 3` | `check_badges()` |
| 7日連続 | `streak_days >= 7` | `check_badges()` |
| 今週10回完了 | 今週の `weekly_stats >= 10` | `check_badges()` |
| 50回達成 | `total_pomodoros >= 50` | `check_badges()` |

**バッジ付与ロジック**

````python
def check_badges(data):
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
````

#### streak_days

連続完了日数。日をまたいで毎日完了すると増加します。

- 型: `integer`
- 最小値: 0
- 更新タイミング: POST `/api/complete` 時

**ストリーク計算ロジック**

````python
if data['last_completion_date']:
    last_date = datetime.fromisoformat(data['last_completion_date'])
    days_diff = (today.date() - last_date.date()).days
    
    if days_diff == 1:
        # 連続
        data['streak_days'] += 1
    elif days_diff > 1:
        # 途切れた
        data['streak_days'] = 1
    # days_diff == 0 の場合は同じ日なのでstreak_daysは変更しない
else:
    data['streak_days'] = 1
````

**例**

| 最後の完了日 | 今日の完了日 | 日数差 | アクション |
|------------|------------|-------|-----------|
| 2026-02-22 | 2026-02-23 | 1 | `streak_days += 1` |
| 2026-02-22 | 2026-02-22 | 0 | 変更なし |
| 2026-02-22 | 2026-02-25 | 3 | `streak_days = 1` (リセット) |
| null | 2026-02-24 | - | `streak_days = 1` (初回) |

#### last_completion_date

最後にポモドーロを完了した日時。ISO 8601形式の文字列。

- 型: `string` (ISO 8601)
- 形式: `YYYY-MM-DDTHH:MM:SS.mmmmmm`
- 例: `"2026-02-24T12:34:56.789012"`
- 更新タイミング: POST `/api/complete` 時

#### daily_stats

日別の完了数を保持する辞書。キーは `YYYY-MM-DD` 形式の日付文字列。

- 型: `object` (辞書)
- キー形式: `YYYY-MM-DD`
- 値の型: `integer`
- 例: `{"2026-02-24": 3, "2026-02-23": 5}`

**更新ロジック**

````python
today = datetime.now()
date_str = today.strftime('%Y-%m-%d')

if date_str not in data['daily_stats']:
    data['daily_stats'][date_str] = 0
data['daily_stats'][date_str] += 1
````

#### weekly_stats

週別の完了数を保持する辞書。キーは `YYYY-W%U` 形式の週番号。

- 型: `object` (辞書)
- キー形式: `YYYY-WNN` (例: `2026-W08`)
- 値の型: `integer`
- 例: `{"2026-W08": 12, "2026-W07": 8}`

**週番号の計算**

````python
week_key = datetime.now().strftime('%Y-W%U')
# %U: 週番号（日曜日を週の始まりとする）
````

**更新ロジック**

````python
week_key = today.strftime('%Y-W%U')

if week_key not in data['weekly_stats']:
    data['weekly_stats'][week_key] = 0
data['weekly_stats'][week_key] += 1
````

#### monthly_stats

月別の完了数を保持する辞書。キーは `YYYY-MM` 形式の年月文字列。

- 型: `object` (辞書)
- キー形式: `YYYY-MM`
- 値の型: `integer`
- 例: `{"2026-02": 15, "2026-01": 25}`

**更新ロジック**

````python
month_key = today.strftime('%Y-%m')

if month_key not in data['monthly_stats']:
    data['monthly_stats'][month_key] = 0
data['monthly_stats'][month_key] += 1
````

## 設定データモデル

### Settings

ユーザーのカスタム設定を保持します。

**ファイル**: `settings.json`

**構造**

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

**フィールド定義**

| フィールド | 型 | 必須 | デフォルト値 | 説明 |
|----------|---|------|-----------|------|
| `focus_duration` | integer | ✓ | 25 | 集中時間（分） |
| `short_break` | integer | ✓ | 5 | 短い休憩時間（分） |
| `long_break` | integer | ✓ | 15 | 長い休憩時間（分） |
| `theme` | string | ✓ | "light" | テーマ |
| `sound_start` | boolean | ✓ | true | 開始音を有効にするか |
| `sound_end` | boolean | ✓ | true | 終了音を有効にするか |
| `sound_tick` | boolean | ✓ | false | Tick音を有効にするか |
| `visual_effects` | boolean | ✓ | true | 背景エフェクトを有効にするか |

### フィールド詳細

#### focus_duration

集中時間の長さ（分単位）。

- 型: `integer`
- デフォルト: `25`
- 選択肢: `15`, `25`, `35`, `45`

#### short_break

短い休憩の長さ（分単位）。

- 型: `integer`
- デフォルト: `5`
- 選択肢: `5`, `10`, `15`

#### long_break

長い休憩の長さ（分単位）。

- 型: `integer`
- デフォルト: `15`
- 選択肢: `15`, `20`, `30`

#### theme

UIのテーマ。

- 型: `string`
- デフォルト: `"light"`
- 選択肢:
  - `"light"`: ライトモード
  - `"dark"`: ダークモード
  - `"focus"`: フォーカスモード（ミニマル）

**テーマの実装**

テーマはCSSクラス（`theme-dark`, `theme-focus`）として body 要素に適用されます。

````javascript
document.body.className = `theme-${settings.theme}`;
````

#### sound_start

タイマー開始時にサウンドを再生するかどうか。

- 型: `boolean`
- デフォルト: `true`
- サウンド: 440Hz (A4)、0.1秒

#### sound_end

タイマー終了時にサウンドを再生するかどうか。

- 型: `boolean`
- デフォルト: `true`
- サウンド: 880Hz (A5)、0.3秒

#### sound_tick

タイマーのTick音を再生するかどうか。

- 型: `boolean`
- デフォルト: `false`
- サウンド: 220Hz、0.01秒

#### visual_effects

背景にパーティクルエフェクトを表示するかどうか。

- 型: `boolean`
- デフォルト: `true`
- 実装: Canvas API によるパーティクルアニメーション

## APIレスポンスモデル

### CompleteResponse

POST `/api/complete` のレスポンスモデル。

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

| フィールド | 型 | 説明 |
|----------|---|------|
| `success` | boolean | 処理が成功したかどうか |
| `xp` | integer | 更新後の累積XP |
| `level` | integer | 更新後のレベル |
| `new_badges` | array[string] | 新しく獲得したバッジのリスト |
| `streak_days` | integer | 更新後の連続日数 |
| `total_pomodoros` | integer | 更新後の累積完了数 |

### StatsResponse

GET `/api/stats` のレスポンスモデル。

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
    }
  ],
  "monthly_data": [
    {
      "date": "2026-02-01",
      "count": 1
    }
  ]
}
````

| フィールド | 型 | 説明 |
|----------|---|------|
| `total_pomodoros` | integer | 累積完了ポモドーロ数 |
| `xp` | integer | 累積経験値 |
| `level` | integer | 現在のレベル |
| `badges` | array[string] | 獲得済みバッジ |
| `streak_days` | integer | 連続日数 |
| `weekly_data` | array[DayData] | 過去7日間のデータ |
| `monthly_data` | array[DayData] | 過去30日間のデータ |

#### DayData

日別の統計データ。

````json
{
  "date": "2026-02-24",
  "count": 3,
  "day": "Mon"
}
````

| フィールド | 型 | 必須 | 説明 |
|----------|---|------|------|
| `date` | string | ✓ | 日付（YYYY-MM-DD形式） |
| `count` | integer | ✓ | その日の完了ポモドーロ数 |
| `day` | string | △ | 曜日の略称（weekly_dataのみ） |

### SettingsResponse

GET `/api/settings` のレスポンスモデル。

Settings モデルと同一です。

### SaveSettingsResponse

POST `/api/settings` のレスポンスモデル。

````json
{
  "success": true
}
````

| フィールド | 型 | 説明 |
|----------|---|------|
| `success` | boolean | 設定の保存に成功したかどうか |

## データの初期化

### デフォルトのユーザーデータ

`user_data.json` が存在しない場合、以下のデフォルト値が使用されます。

````python
{
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
````

### デフォルトの設定

`settings.json` が存在しない場合、以下のデフォルト値が使用されます。

````python
{
    'focus_duration': 25,
    'short_break': 5,
    'long_break': 15,
    'theme': 'light',
    'sound_start': True,
    'sound_end': True,
    'sound_tick': False,
    'visual_effects': True
}
````

## データの永続化

### 保存タイミング

#### ユーザーデータ

- POST `/api/complete` 時に保存
- ポモドーロ完了ごとに更新

#### 設定データ

- POST `/api/settings` 時に保存
- ユーザーが「設定を保存」ボタンをクリックした時のみ

### 保存形式

両方のファイルはJSONフォーマットで保存されます。

- エンコーディング: UTF-8
- インデント: 2スペース
- `ensure_ascii=False`: 日本語を直接保存

````python
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
````

## バリデーション

現在、入力バリデーションは実装されていません。クライアント側のHTML要素（select, checkbox）により、一定の範囲制約はありますが、APIレベルでの検証はありません。

**改善の余地**

- 設定値の範囲チェック
- 必須フィールドの存在チェック
- データ型の検証
- 不正なバッジ名の除外

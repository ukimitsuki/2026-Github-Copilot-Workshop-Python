# フロントエンド仕様

このドキュメントは、ポモドーロタイマーアプリケーションのフロントエンド実装の詳細を記載しています。

## 目次

- [概要](#概要)
- [HTML構造](#html構造)
- [CSS設計](#css設計)
- [JavaScript実装](#javascript実装)
- [ビジュアルエフェクト](#ビジュアルエフェクト)
- [サウンドシステム](#サウンドシステム)

## 概要

フロントエンドは単一の HTML ファイル（`templates/index.html`）にすべてのコードが含まれています。

**技術スタック**

- HTML5
- CSS3（CSS変数、Flexbox、Grid）
- Vanilla JavaScript（ES6+）
- Canvas API（パーティクルアニメーション）
- Web Audio API（サウンド生成）

**主要な機能**

- タイマー機能（開始、一時停止、リセット）
- 3つのモード切り替え（集中時間、短い休憩、長い休憩）
- ゲーミフィケーション表示（XP、レベル、バッジ、ストリーク）
- 設定のカスタマイズ
- 統計グラフ表示
- テーマ切り替え
- パーティクルアニメーション
- サウンドエフェクト

## HTML構造

### 全体構造

````html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ポモドーロタイマー</title>
    <style>...</style>
</head>
<body>
    <canvas id="particles-canvas"></canvas>
    
    <div class="container">
        <header>
            <h1>🍅 ポモドーロタイマー</h1>
        </header>
        
        <div class="main-content">
            <!-- タイマーセクション -->
            <div class="card timer-section">...</div>
            
            <!-- タブセクション -->
            <div class="card">...</div>
        </div>
    </div>
    
    <script>...</script>
</body>
</html>
````

### セクション詳細

#### 1. パーティクルキャンバス

背景エフェクト用のCanvasエレメント。

````html
<canvas id="particles-canvas"></canvas>
````

- 固定位置（`position: fixed`）
- z-index: -1（背景に配置）
- 不透明度: 0.3

#### 2. ヘッダー

````html
<header>
    <h1>🍅 ポモドーロタイマー</h1>
</header>
````

#### 3. タイマーセクション（左カラム）

````html
<div class="card timer-section">
    <!-- 円形プログレスバー -->
    <div class="progress-ring">
        <svg width="300" height="300">
            <circle class="progress-ring-circle" .../>
        </svg>
        <div class="timer-display" id="timer-display">25:00</div>
    </div>
    
    <!-- 制御ボタン -->
    <div class="controls">
        <button id="start-btn">開始</button>
        <button id="pause-btn" class="secondary" disabled>一時停止</button>
        <button id="reset-btn" class="danger">リセット</button>
    </div>
    
    <!-- モード選択 -->
    <div class="setting-item">
        <label>タイマーモード</label>
        <select id="mode-select">
            <option value="focus">集中時間</option>
            <option value="short-break">短い休憩</option>
            <option value="long-break">長い休憩</option>
        </select>
    </div>
</div>
````

**主要なエレメント**

| ID | 要素 | 用途 |
|---|-----|------|
| `timer-display` | div | タイマー表示（MM:SS形式） |
| `start-btn` | button | タイマー開始 |
| `pause-btn` | button | タイマー一時停止 |
| `reset-btn` | button | タイマーリセット |
| `mode-select` | select | モード選択 |

#### 4. タブセクション（右カラム）

````html
<div class="card">
    <!-- タブボタン -->
    <div class="tabs">
        <button class="tab-button active">ゲーミフィケーション</button>
        <button class="tab-button">設定</button>
        <button class="tab-button">統計</button>
    </div>
    
    <!-- タブコンテンツ -->
    <div id="gamification-tab" class="tab-content active">...</div>
    <div id="settings-tab" class="tab-content">...</div>
    <div id="stats-tab" class="tab-content">...</div>
</div>
````

##### ゲーミフィケーションタブ

````html
<div id="gamification-tab" class="tab-content active">
    <!-- レベル表示 -->
    <div class="level-display">
        レベル <span id="level">1</span>
    </div>
    
    <!-- XPバー -->
    <div class="xp-bar">
        <div class="xp-fill" id="xp-fill" style="width: 0%">
            <span id="xp-text">0 / 100 XP</span>
        </div>
    </div>
    
    <!-- 統計カード -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" id="total-pomodoros">0</div>
            <div class="stat-label">完了したポモドーロ</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="streak-days">0</div>
            <div class="stat-label">連続日数 🔥</div>
        </div>
    </div>
    
    <!-- バッジ -->
    <div class="badges-container" id="badges-container">
        <p style="opacity: 0.6;">バッジはまだありません</p>
    </div>
</div>
````

**主要なエレメント**

| ID | 要素 | 用途 |
|---|-----|------|
| `level` | span | レベル表示 |
| `xp-fill` | div | XPバーの塗りつぶし |
| `xp-text` | span | XPテキスト（"X / 100 XP"） |
| `total-pomodoros` | div | 累積完了数 |
| `streak-days` | div | 連続日数 |
| `badges-container` | div | バッジのコンテナ |

##### 設定タブ

````html
<div id="settings-tab" class="tab-content">
    <!-- 時間設定 -->
    <div class="settings-group">
        <h3>⏱️ 時間設定</h3>
        <select id="focus-duration">...</select>
        <select id="short-break">...</select>
        <select id="long-break">...</select>
    </div>
    
    <!-- テーマ -->
    <div class="settings-group">
        <h3>🎨 テーマ</h3>
        <select id="theme-select">...</select>
    </div>
    
    <!-- サウンド -->
    <div class="settings-group">
        <h3>🔊 サウンド</h3>
        <input type="checkbox" id="sound-start" checked>
        <input type="checkbox" id="sound-end" checked>
        <input type="checkbox" id="sound-tick">
    </div>
    
    <!-- ビジュアルエフェクト -->
    <div class="settings-group">
        <h3>✨ ビジュアルエフェクト</h3>
        <input type="checkbox" id="visual-effects" checked>
    </div>
    
    <button onclick="saveSettings()">設定を保存</button>
</div>
````

**主要なエレメント**

| ID | 要素 | 用途 |
|---|-----|------|
| `focus-duration` | select | 集中時間の選択 |
| `short-break` | select | 短い休憩時間の選択 |
| `long-break` | select | 長い休憩時間の選択 |
| `theme-select` | select | テーマの選択 |
| `sound-start` | checkbox | 開始音の有効/無効 |
| `sound-end` | checkbox | 終了音の有効/無効 |
| `sound-tick` | checkbox | Tick音の有効/無効 |
| `visual-effects` | checkbox | エフェクトの有効/無効 |

##### 統計タブ

````html
<div id="stats-tab" class="tab-content">
    <!-- 週間統計 -->
    <div class="settings-group">
        <h3>📊 週間統計</h3>
        <div class="chart-container">
            <div class="chart-bars" id="weekly-chart"></div>
        </div>
    </div>
    
    <!-- 今月の統計 -->
    <div class="settings-group">
        <h3>📈 今月の統計</h3>
        <div class="stat-card">
            <div class="stat-value" id="month-total">0</div>
            <div class="stat-label">今月の完了数</div>
        </div>
    </div>
</div>
````

**主要なエレメント**

| ID | 要素 | 用途 |
|---|-----|------|
| `weekly-chart` | div | 週間バーチャート |
| `month-total` | div | 今月の完了数 |

## CSS設計

### CSS変数

テーマシステムはCSS変数を使用して実装されています。

````css
:root {
    --bg-color: #f5f5f5;
    --text-color: #333;
    --card-bg: #ffffff;
    --primary-color: #4CAF50;
    --secondary-color: #2196F3;
    --danger-color: #f44336;
}

/* ダークテーマ */
body.theme-dark {
    --bg-color: #1a1a1a;
    --text-color: #e0e0e0;
    --card-bg: #2d2d2d;
}

/* フォーカスモード */
body.theme-focus {
    --bg-color: #000000;
    --text-color: #ffffff;
    --card-bg: #1a1a1a;
}
````

**変数一覧**

| 変数名 | 説明 | ライト | ダーク | フォーカス |
|-------|------|--------|--------|----------|
| `--bg-color` | 背景色 | #f5f5f5 | #1a1a1a | #000000 |
| `--text-color` | テキスト色 | #333 | #e0e0e0 | #ffffff |
| `--card-bg` | カード背景色 | #ffffff | #2d2d2d | #1a1a1a |
| `--primary-color` | プライマリ色 | #4CAF50 | #4CAF50 | #4CAF50 |
| `--secondary-color` | セカンダリ色 | #2196F3 | #2196F3 | #2196F3 |
| `--danger-color` | 危険色 | #f44336 | #f44336 | #f44336 |

### レイアウト

#### グリッドレイアウト

````css
.main-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
    margin-bottom: 30px;
}

@media (max-width: 768px) {
    .main-content {
        grid-template-columns: 1fr;
    }
}
````

- デスクトップ: 2カラムグリッド
- モバイル（768px以下）: 1カラム

#### 円形プログレスバー

SVGを使用した円形プログレスバー。

````css
.progress-ring {
    position: relative;
    width: 300px;
    height: 300px;
    margin: 0 auto 30px;
}

.progress-ring svg {
    transform: rotate(-90deg);
}

.progress-ring-circle {
    transition: stroke-dashoffset 0.3s ease, stroke 0.5s ease;
}
````

**SVG属性**

````html
<circle
    cx="150"
    cy="150"
    r="140"
    stroke="#2196F3"
    stroke-width="20"
    fill="none"
    stroke-dasharray="880"
    stroke-dashoffset="0"
    stroke-linecap="round"
/>
````

- 半径: 140px
- 円周: 880px（2πr = 2 × π × 140 ≈ 880）
- `stroke-dashoffset` で進捗を制御

### アニメーション

#### バッジ出現アニメーション

````css
.badge {
    animation: badgeAppear 0.5s ease;
}

@keyframes badgeAppear {
    from {
        opacity: 0;
        transform: scale(0);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
````

#### 通知スライドイン

````css
.notification {
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
````

## JavaScript実装

### グローバル変数

````javascript
let timerInterval = null;       // タイマーのインターバルID
let timeLeft = 25 * 60;         // 残り時間（秒）
let totalTime = 25 * 60;        // 総時間（秒）
let isRunning = false;          // タイマーが動作中か
let currentMode = 'focus';      // 現在のモード
let settings = {};              // 設定オブジェクト
let particlesAnimation = null;  // パーティクルアニメーションID
let audioContext = null;        // Web Audio API コンテキスト
````

### 初期化フロー

````javascript
async function init() {
    await loadSettings();       // 設定を読み込み
    await loadStats();          // 統計を読み込み
    applySettings();            // 設定を適用
    updateDisplay();            // 表示を更新
    initParticles();            // パーティクルを初期化
    // AudioContextの初期化
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
}

// ページ読み込み時に初期化
init();
````

**初期化順序**

1. 設定をAPIから取得
2. 統計をAPIから取得
3. 設定をUIに適用（テーマ、時間など）
4. タイマー表示を更新
5. パーティクルアニメーション開始
6. AudioContextを作成

### タイマー機能

#### 開始

````javascript
function startTimer() {
    if (!isRunning) {
        isRunning = true;
        document.getElementById('start-btn').disabled = true;
        document.getElementById('pause-btn').disabled = false;
        
        // 開始音を再生
        if (settings.sound_start) {
            playSound('start');
        }
        
        timerInterval = setInterval(() => {
            timeLeft--;
            updateDisplay();
            updateProgressRing();
            
            // Tick音を再生
            if (settings.sound_tick) {
                playSound('tick');
            }
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                isRunning = false;
                
                // 終了音を再生
                if (settings.sound_end) {
                    playSound('end');
                }
                
                // 集中時間完了時のみAPIを呼び出し
                if (currentMode === 'focus') {
                    completePomodoro();
                }
                
                showNotification('タイマー完了！');
                document.getElementById('start-btn').disabled = false;
                document.getElementById('pause-btn').disabled = true;
            }
        }, 1000);
    }
}
````

**処理フロー**

1. ボタンの状態を更新（開始を無効化、一時停止を有効化）
2. 開始音を再生
3. 1秒ごとのインターバルを設定
4. 毎秒実行:
   - `timeLeft` を減算
   - 表示を更新
   - プログレスリングを更新
   - Tick音を再生（有効な場合）
5. タイマーが0になったら:
   - インターバルをクリア
   - 終了音を再生
   - 集中モードの場合、`completePomodoro()` を呼び出し
   - 通知を表示

#### 一時停止

````javascript
function pauseTimer() {
    if (isRunning) {
        clearInterval(timerInterval);
        isRunning = false;
        document.getElementById('start-btn').disabled = false;
        document.getElementById('pause-btn').disabled = true;
    }
}
````

#### リセット

````javascript
function resetTimer() {
    clearInterval(timerInterval);
    isRunning = false;
    
    // 現在のモードに応じた時間を設定
    if (currentMode === 'focus') {
        timeLeft = settings.focus_duration * 60;
        totalTime = settings.focus_duration * 60;
    } else if (currentMode === 'short-break') {
        timeLeft = settings.short_break * 60;
        totalTime = settings.short_break * 60;
    } else if (currentMode === 'long-break') {
        timeLeft = settings.long_break * 60;
        totalTime = settings.long_break * 60;
    }
    
    updateDisplay();
    updateProgressRing();
    document.getElementById('start-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;
}
````

#### モード切り替え

````javascript
function changeMode() {
    const modeSelect = document.getElementById('mode-select');
    currentMode = modeSelect.value;
    resetTimer();
}
````

### 表示更新

#### タイマー表示

````javascript
function updateDisplay() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    const display = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    document.getElementById('timer-display').textContent = display;
}
````

- MM:SS 形式
- 秒は常に2桁表示（例: `25:05`）

#### プログレスリング

````javascript
function updateProgressRing() {
    const circle = document.querySelector('.progress-ring-circle');
    const circumference = 880; // 2πr
    const offset = circumference - (timeLeft / totalTime) * circumference;
    circle.style.strokeDashoffset = offset;
    
    // 色の変化（青→黄→赤）
    const progress = timeLeft / totalTime;
    if (progress > 0.5) {
        circle.style.stroke = '#2196F3'; // 青
    } else if (progress > 0.2) {
        circle.style.stroke = '#FFC107'; // 黄
    } else {
        circle.style.stroke = '#f44336'; // 赤
    }
}
````

**色の変化**

| 残り時間 | 色 | 意味 |
|---------|---|------|
| 50%以上 | 青 (#2196F3) | 余裕あり |
| 20-50% | 黄 (#FFC107) | 注意 |
| 20%未満 | 赤 (#f44336) | 終了間近 |

### API通信

#### ポモドーロ完了

````javascript
async function completePomodoro() {
    try {
        const response = await fetch('/api/complete', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (result.success) {
            // UIを更新
            document.getElementById('level').textContent = result.level;
            document.getElementById('total-pomodoros').textContent = result.total_pomodoros;
            document.getElementById('streak-days').textContent = result.streak_days;
            
            // XPバーを更新
            const xpProgress = (result.xp % 100);
            const xpFill = document.getElementById('xp-fill');
            xpFill.style.width = xpProgress + '%';
            document.getElementById('xp-text').textContent = 
                `${xpProgress} / 100 XP`;
            
            // 新しいバッジを表示
            if (result.new_badges.length > 0) {
                result.new_badges.forEach(badge => {
                    showNotification(`🏆 新しいバッジ獲得: ${badge}`);
                });
                await loadStats(); // バッジリストを更新
            }
        }
    } catch (error) {
        console.error('完了処理に失敗:', error);
    }
}
````

#### 統計読み込み

````javascript
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        // ゲーミフィケーション情報を更新
        document.getElementById('level').textContent = stats.level;
        document.getElementById('total-pomodoros').textContent = stats.total_pomodoros;
        document.getElementById('streak-days').textContent = stats.streak_days;
        
        // XPバーを更新
        const xpProgress = (stats.xp % 100);
        const xpFill = document.getElementById('xp-fill');
        xpFill.style.width = xpProgress + '%';
        document.getElementById('xp-text').textContent = 
            `${xpProgress} / 100 XP`;
        
        // バッジを表示
        const badgesContainer = document.getElementById('badges-container');
        if (stats.badges.length > 0) {
            badgesContainer.innerHTML = stats.badges
                .map(badge => `<div class="badge">${badge}</div>`)
                .join('');
        } else {
            badgesContainer.innerHTML = 
                '<p style="opacity: 0.6;">バッジはまだありません</p>';
        }
        
        // 週間チャートを更新
        const weeklyChart = document.getElementById('weekly-chart');
        const maxCount = Math.max(...stats.weekly_data.map(d => d.count), 1);
        weeklyChart.innerHTML = stats.weekly_data.map(day => {
            const height = (day.count / maxCount) * 100;
            return `<div class="chart-bar" style="height: ${height}%">
                <div class="chart-label">${day.day}</div>
            </div>`;
        }).join('');
        
        // 今月の統計
        const monthTotal = stats.monthly_data.reduce((sum, day) => 
            sum + day.count, 0);
        document.getElementById('month-total').textContent = monthTotal;
        
    } catch (error) {
        console.error('統計の読み込みに失敗:', error);
    }
}
````

#### 設定の読み込みと保存

````javascript
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        settings = await response.json();
        
        // UIに設定を反映
        document.getElementById('focus-duration').value = settings.focus_duration;
        document.getElementById('short-break').value = settings.short_break;
        document.getElementById('long-break').value = settings.long_break;
        document.getElementById('theme-select').value = settings.theme;
        document.getElementById('sound-start').checked = settings.sound_start;
        document.getElementById('sound-end').checked = settings.sound_end;
        document.getElementById('sound-tick').checked = settings.sound_tick;
        document.getElementById('visual-effects').checked = settings.visual_effects;
    } catch (error) {
        console.error('設定の読み込みに失敗:', error);
    }
}

async function saveSettings() {
    // UIから設定を収集
    settings = {
        focus_duration: parseInt(document.getElementById('focus-duration').value),
        short_break: parseInt(document.getElementById('short-break').value),
        long_break: parseInt(document.getElementById('long-break').value),
        theme: document.getElementById('theme-select').value,
        sound_start: document.getElementById('sound-start').checked,
        sound_end: document.getElementById('sound-end').checked,
        sound_tick: document.getElementById('sound-tick').checked,
        visual_effects: document.getElementById('visual-effects').checked
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        const result = await response.json();
        
        if (result.success) {
            applySettings();
            resetTimer(); // タイマーをリセットして新しい時間を適用
            showNotification('設定を保存しました');
        }
    } catch (error) {
        console.error('設定の保存に失敗:', error);
    }
}

function applySettings() {
    // テーマを適用
    document.body.className = `theme-${settings.theme}`;
    
    // パーティクルエフェクトの表示/非表示
    const canvas = document.getElementById('particles-canvas');
    canvas.style.display = settings.visual_effects ? 'block' : 'none';
}
````

### タブ切り替え

````javascript
function switchTab(tabName, event) {
    // すべてのタブを非アクティブ化
    document.querySelectorAll('.tab-button').forEach(btn => 
        btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => 
        content.classList.remove('active'));
    
    // 選択されたタブをアクティブ化
    event.target.classList.add('active');
    document.getElementById(tabName + '-tab').classList.add('active');
    
    // 統計タブの場合は最新データを読み込み
    if (tabName === 'stats') {
        loadStats();
    }
}
````

### 通知システム

````javascript
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
````

**動作**

1. 通知要素を作成
2. メッセージを設定
3. DOMに追加（スライドインアニメーション）
4. 3秒後にスライドアウト
5. アニメーション完了後に削除

## ビジュアルエフェクト

### パーティクルアニメーション

Canvas APIを使用したパーティクルエフェクト。

````javascript
function initParticles() {
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    const particleCount = 50;
    
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2 + 1;
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(33, 150, 243, 0.5)';
            ctx.fill();
        }
    }
    
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        // パーティクル間の線を描画
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = 
                        `rgba(33, 150, 243, ${0.2 * (1 - distance / 100)})`;
                    ctx.stroke();
                }
            }
        }
        
        particlesAnimation = requestAnimationFrame(animate);
    }
    
    animate();
    
    // ウィンドウリサイズ対応
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}
````

**特徴**

- 50個のパーティクル
- ランダムな位置と速度で初期化
- 画面端で反射
- パーティクル間が100px以内の場合、線を描画
- 線の不透明度は距離に応じて変化

## サウンドシステム

### Web Audio API

ビープ音を生成するためにWeb Audio APIを使用。

````javascript
// AudioContextの初期化（ユーザーアクション後）
audioContext = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
    if (!audioContext) {
        return;
    }
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    if (type === 'start') {
        oscillator.frequency.value = 440; // A4
        gainNode.gain.value = 0.3;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
    } else if (type === 'end') {
        oscillator.frequency.value = 880; // A5
        gainNode.gain.value = 0.3;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    } else if (type === 'tick') {
        oscillator.frequency.value = 220;
        gainNode.gain.value = 0.05;
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.01);
    }
}
````

**サウンド仕様**

| タイプ | 周波数 | 音量 | 長さ | 説明 |
|-------|-------|------|------|------|
| start | 440 Hz | 0.3 | 0.1秒 | タイマー開始音（A4） |
| end | 880 Hz | 0.3 | 0.3秒 | タイマー終了音（A5） |
| tick | 220 Hz | 0.05 | 0.01秒 | 毎秒のTick音 |

**注意事項**

- AudioContextはユーザーアクション後に初期化される必要がある（ブラウザのポリシー）
- `init()` 関数内で初期化

## パフォーマンス考慮事項

### 最適化

1. **パーティクルアニメーション**
   - `requestAnimationFrame` を使用
   - 設定で無効化可能

2. **タイマー更新**
   - 1秒ごとの更新（`setInterval`）
   - DOM操作を最小限に

3. **API呼び出し**
   - 必要な時のみ呼び出し
   - 統計タブを開いた時のみ `loadStats()` を実行

### ブラウザ互換性

- **AudioContext**: `window.AudioContext || window.webkitAudioContext`
- **ES6+**: 最新のブラウザを想定
- **CSS Grid/Flexbox**: モダンブラウザのみ

## まとめ

フロントエンドはシンプルなバニラJavaScriptで実装されており、フレームワークに依存しない軽量な設計となっています。REST APIを通じてバックエンドと通信し、ステートレスなアーキテクチャを維持しています。

/**
 * ポモドーロタイマー - メインアプリケーション
 * 
 * UI と Timer を統合し、ユーザーインタラクションを処理
 */

class PomodoroApp {
    /**
     * アプリを初期化
     */
    constructor() {
        // DOM 要素
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            resetBtn: document.getElementById('resetBtn'),
            skipBtn: document.getElementById('skipBtn'),
            timerDisplay: document.getElementById('timerDisplay'),
            modeLabel: document.getElementById('modeLabel'),
            progressCircle: document.getElementById('progressCircle'),
            sessionsCompleted: document.getElementById('sessionsCompleted'),
            totalFocusTime: document.getElementById('totalFocusTime'),
        };

        // 設定（デフォルト）
        this.config = {
            workDuration: 25 * 60, // 25分
            shortBreakDuration: 5 * 60, // 5分
            longBreakDuration: 15 * 60, // 15分
            longBreakInterval: 4, // 4セッションごと
        };

        // ステート
        this.sessionCount = 0; // 完了したセッション数
        this.totalFocusSeconds = 0; // 合計集中時間（秒）
        this.currentMode = 'work'; // 'work' | 'short_break' | 'long_break'

        // Timer インスタンス
        this.timer = new Timer(this.config.workDuration);

        // イベント設定
        this._setupEventListeners();

        // 復元可能な状態を復元
        this._restoreState();

        // 初期表示
        this._updateDisplay();

        // ブラウザ通知の許可をリクエスト
        notificationManager.requestNotificationPermission();
    }

    /**
     * イベントリスナーを設定
     */
    _setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this._toggleStart());
        this.elements.resetBtn.addEventListener('click', () => this._reset());
        this.elements.skipBtn.addEventListener('click', () => this._skip());

        // 設定パネル
        document.getElementById('applySettingsBtn').addEventListener('click', 
            () => this._applySettings());

        // キーボードショートカット
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                this._toggleStart();
            } else if (e.code === 'KeyR') {
                e.preventDefault();
                this._reset();
            } else if (e.code === 'KeyS') {
                e.preventDefault();
                this._skip();
            }
        });

        // Timer コールバック
        this.timer.onTick = () => this._updateDisplay();
        this.timer.onComplete = () => this._onSessionComplete();
    }

    /**
     * 開始/一時停止を切り替え
     */
    _toggleStart() {
        if (this.timer.isRunning) {
            this.timer.pause();
        } else {
            this.timer.start();
        }
        this._updateDisplay();
        this._saveState();
    }

    /**
     * タイマーをリセット
     */
    _reset() {
        this.timer.reset();
        this._updateDisplay();
        this._saveState();
    }

    /**
     * 次のモードへスキップ
     */
    _skip() {
        if (this.timer.isRunning) {
            this.timer.pause();
        }
        this._switchMode();
        this._updateDisplay();
        this._saveState();
    }

    /**
     * 設定を適用
     */
    _applySettings() {
        const workDuration = parseInt(document.getElementById('workDuration').value) * 60;
        const shortBreakDuration = parseInt(document.getElementById('shortBreakDuration').value) * 60;
        const longBreakDuration = parseInt(document.getElementById('longBreakDuration').value) * 60;
        const longBreakInterval = parseInt(document.getElementById('longBreakInterval').value);
        const autoStart = document.getElementById('autoStartToggle').checked;
        const soundEnabled = document.getElementById('soundToggle').checked;
        const notificationEnabled = document.getElementById('notificationToggle').checked;

        // 設定を更新
        this.config.workDuration = workDuration;
        this.config.shortBreakDuration = shortBreakDuration;
        this.config.longBreakDuration = longBreakDuration;
        this.config.longBreakInterval = longBreakInterval;
        this.config.autoStart = autoStart;

        // 通知設定を適用
        notificationManager.setSettings(soundEnabled, notificationEnabled);

        // ローカルストレージに保存
        appStorage.saveConfig(this.config);

        // 現在のタイマーを再初期化
        this.timer.reset();
        const durations = {
            work: this.config.workDuration,
            short_break: this.config.shortBreakDuration,
            long_break: this.config.longBreakDuration,
        };
        this.timer = new Timer(durations[this.currentMode], this.timer.nowFn);
        this.timer.onTick = () => this._updateDisplay();
        this.timer.onComplete = () => this._onSessionComplete();

        this._updateDisplay();
    }

    /**
     * セッション完了時の処理
     */
    _onSessionComplete() {
        if (this.currentMode === 'work') {
            this.sessionCount++;
            this.totalFocusSeconds += this.config.workDuration;

            // サーバーにセッションをPOST
            this._postSessionToServer();
        }

        // モード切替
        this._switchMode();
        this._updateDisplay();
        this._saveState();

        // 通知
        const modeLabels = {
            work: '作業中',
            short_break: '短休憩中',
            long_break: '長休憩中',
        };

        notificationManager.playBell();
        notificationManager.notify('セッション完了', {
            body: `次は ${modeLabels[this.currentMode]} です`,
            tag: 'pomodoro-notification',
        });
    }

    /**
     * セッションをサーバーに送信
     */
    _postSessionToServer() {
        const now = Math.floor(Date.now() / 1000);
        const startTs = now - this.config.workDuration;

        const data = {
            start_ts: startTs,
            end_ts: now,
            duration_sec: this.config.workDuration,
            kind: 'work',
        };

        fetch('/api/session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP Error: ${response.status}`);
                }
                return response.json();
            })
            .then((result) => {
                console.log('セッションがサーバーに保存されました:', result);
            })
            .catch((error) => {
                console.error('セッション保存エラー:', error);
                // TODO: ローカルキューに保管して再送
            });
    }


    /**
     * モードを切り替え
     */
    _switchMode() {
        if (this.currentMode === 'work') {
            // 長休憩の判定
            if (this.sessionCount % this.config.longBreakInterval === 0) {
                this.currentMode = 'long_break';
                this.timer = new Timer(this.config.longBreakDuration, this.timer.nowFn);
            } else {
                this.currentMode = 'short_break';
                this.timer = new Timer(this.config.shortBreakDuration, this.timer.nowFn);
            }
        } else {
            this.currentMode = 'work';
            this.timer = new Timer(this.config.workDuration, this.timer.nowFn);
        }

        // コールバックを再設定
        this.timer.onTick = () => this._updateDisplay();
        this.timer.onComplete = () => this._onSessionComplete();
    }

    /**
     * 表示を更新
     */
    _updateDisplay() {
        const remaining = this.timer.getRemainingSeconds();
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining % 60;

        // タイマー表示
        this.elements.timerDisplay.textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        // モードラベル
        const modeLabels = {
            work: '作業中',
            short_break: '短休憩中',
            long_break: '長休憩中',
        };
        this.elements.modeLabel.textContent = modeLabels[this.currentMode];

        // プログレスバー
        const progress = this.timer.getProgress();
        const circumference = 2 * Math.PI * 90; // 半径 90
        const offset = circumference * (1 - progress);
        this.elements.progressCircle.style.strokeDashoffset = offset;

        // ボタンテキスト
        this.elements.startBtn.textContent = 
            this.timer.isRunning ? '一時停止' : '開始';

        // 今日の進捗
        this.elements.sessionsCompleted.textContent = this.sessionCount;
        const totalHours = Math.floor(this.totalFocusSeconds / 3600);
        const totalMinutes = Math.floor((this.totalFocusSeconds % 3600) / 60);
        this.elements.totalFocusTime.textContent = `${totalHours}時間${totalMinutes}分`;
    }

    /**
     * 状態を保存
     */
    _saveState() {
        appStorage.saveSession({
            currentMode: this.currentMode,
            sessionCount: this.sessionCount,
            totalFocusSeconds: this.totalFocusSeconds,
            timerIsRunning: this.timer.isRunning,
            timerRemainingSeconds: this.timer.getRemainingSeconds(),
            timerPausedTime: this.timer.pausedTime,
            timerStartTime: this.timer.startTime,
        });
    }

    /**
     * 状態を復元
     */
    _restoreState() {
        const stored = appStorage.restoreSession();
        if (!stored) return;

        this.currentMode = stored.currentMode;
        this.sessionCount = stored.sessionCount;
        this.totalFocusSeconds = stored.totalFocusSeconds;

        // Timer を復元
        const durations = {
            work: this.config.workDuration,
            short_break: this.config.shortBreakDuration,
            long_break: this.config.longBreakDuration,
        };
        this.timer = new Timer(durations[this.currentMode]);
        this.timer.pausedTime = stored.timerPausedTime;
        this.timer.startTime = stored.timerStartTime;

        // if (stored.timerIsRunning) {
        //     this.timer.start();
        // }

        // 設定を復元
        const savedConfig = appStorage.restoreConfig();
        if (savedConfig) {
            this.config = savedConfig;
            // UI の設定値も更新
            document.getElementById('workDuration').value = this.config.workDuration / 60;
            document.getElementById('shortBreakDuration').value = this.config.shortBreakDuration / 60;
            document.getElementById('longBreakDuration').value = this.config.longBreakDuration / 60;
            document.getElementById('longBreakInterval').value = this.config.longBreakInterval;
        }
    }
}

// ページ読み込み時にアプリを初期化
window.addEventListener('DOMContentLoaded', () => {
    window.app = new PomodoroApp();
});

/**
 * ポモドーロタイマー - Timer クラス
 * 
 * 特徴:
 * - now() 関数を注入可能で、テストしやすい設計
 * - 一時停止・再開に対応
 * - 時刻ズレを考慮した実装
 */

class Timer {
    /**
     * Timer を初期化
     * @param {number} initialSeconds - 初期時間（秒）
     * @param {Function} nowFn - 現在時刻を返す関数（デフォルト: Date.now）
     */
    constructor(initialSeconds, nowFn = () => Date.now()) {
        this.initialSeconds = initialSeconds;
        this.nowFn = nowFn;

        // ステート
        this.isRunning = false;
        this.startTime = null; // start() 時の時刻
        this.pausedTime = 0; // 一時停止時の経過時間（ミリ秒）
        this.pauseStartTime = null; // 一時停止開始時刻

        // コールバック
        this.onTick = null;
        this.onComplete = null;

        // RAF ハンドル
        this.rafHandle = null;
    }

    /**
     * タイマーを開始
     */
    start() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.startTime = this.nowFn() - this.pausedTime;
        this.pauseStartTime = null;

        this._loop();
    }

    /**
     * タイマーを一時停止
     */
    pause() {
        if (!this.isRunning) return;

        this.isRunning = false;
        this.pauseStartTime = this.nowFn();
        if (this.rafHandle) {
            cancelAnimationFrame(this.rafHandle);
            this.rafHandle = null;
        }
    }

    /**
     * タイマーをリセット
     */
    reset() {
        this.pause();
        this.pausedTime = 0;
        this.startTime = null;
        this.pauseStartTime = null;
        if (this.onTick) {
            this.onTick();
        }
    }

    /**
     * 現在の経過時間（ミリ秒）を取得
     */
    getElapsedMilliseconds() {
        if (this.isRunning) {
            return this.nowFn() - this.startTime;
        }
        return this.pausedTime;
    }

    /**
     * 残り時間（秒）を取得
     */
    getRemainingSeconds() {
        const elapsedMs = this.getElapsedMilliseconds();
        const elapsedSec = Math.floor(elapsedMs / 1000);
        const remaining = Math.max(0, this.initialSeconds - elapsedSec);
        return remaining;
    }

    /**
     * プログレス比率（0-1）を取得
     */
    getProgress() {
        const elapsed = this.getRemainingSeconds();
        return Math.max(0, Math.min(1, (this.initialSeconds - elapsed) / this.initialSeconds));
    }

    /**
     * タイマーが実行中かを取得
     */
    isRunning_() {
        return this.isRunning;
    }

    /**
     * 内部: アニメーションループ
     */
    _loop() {
        if (!this.isRunning) return;

        const remaining = this.getRemainingSeconds();

        if (this.onTick) {
            this.onTick();
        }

        if (remaining <= 0) {
            this.pause();
            if (this.onComplete) {
                this.onComplete();
            }
            return;
        }

        this.rafHandle = requestAnimationFrame(() => this._loop());
    }
}

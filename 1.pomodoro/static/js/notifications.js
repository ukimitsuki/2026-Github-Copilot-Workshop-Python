/**
 * ポモドーロタイマー - 通知とサウンド
 * 
 * Web Notifications API とサウンド再生を実装
 */

class NotificationManager {
    constructor() {
        this.soundEnabled = true;
        this.notificationEnabled = true;
        this.audioContext = null;
    }

    /**
     * ブラウザ通知の許可をリクエスト
     */
    async requestNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission !== 'granted') {
                try {
                    const result = await Notification.requestPermission();
                    return result === 'granted';
                } catch (e) {
                    console.error('通知リクエストエラー:', e);
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * ブラウザ通知を送信
     */
    notify(title, options = {}) {
        if (!this.notificationEnabled || !('Notification' in window)) {
            return;
        }

        if (Notification.permission === 'granted') {
            new Notification(title, {
                icon: '/static/img/icon.png',
                badge: '/static/img/badge.png',
                ...options,
            });
        }
    }

    /**
     * ベルサウンドを再生
     */
    playBell() {
        if (!this.soundEnabled) {
            return;
        }

        // Web Audio API を使用してビープ音を生成
        try {
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            const ctx = this.audioContext;
            const now = ctx.currentTime;

            // ビープ音のパラメータ
            const oscillator = ctx.createOscillator();
            const gain = ctx.createGain();

            oscillator.connect(gain);
            gain.connect(ctx.destination);

            // 周波数とデュレーション
            oscillator.frequency.setValueAtTime(800, now);
            oscillator.frequency.exponentialRampToValueAtTime(600, now + 0.1);

            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0, now + 0.1);

            oscillator.start(now);
            oscillator.stop(now + 0.1);
        } catch (e) {
            console.error('サウンド再生エラー:', e);
        }
    }

    /**
     * 設定を更新
     */
    setSettings(soundEnabled, notificationEnabled) {
        this.soundEnabled = soundEnabled;
        this.notificationEnabled = notificationEnabled;
    }
}

// グローバルインスタンス
const notificationManager = new NotificationManager();

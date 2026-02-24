/**
 * ポモドーロタイマー - Storage ラッパー
 * 
 * localStorage への読み書きを抽象化
 * テスト時はメモリベースのストレージに置換可能
 */

class AppStorage {
    /**
     * ストレージの初期化
     * @param {Object} backendStorage - 実装するストレージ（デフォルト: window.localStorage）
     */
    constructor(backendStorage = window.localStorage) {
        this.backend = backendStorage;
    }

    /**
     * セッション状態を保存
     * @param {Object} state - { isRunning, remainingSeconds, pausedTime }
     */
    saveSession(state) {
        try {
            this.backend.setItem('pomodoro_session', JSON.stringify(state));
        } catch (e) {
            console.error('Failed to save session:', e);
        }
    }

    /**
     * セッション状態を復元
     */
    restoreSession() {
        try {
            const stored = this.backend.getItem('pomodoro_session');
            return stored ? JSON.parse(stored) : null;
        } catch (e) {
            console.error('Failed to restore session:', e);
            return null;
        }
    }

    /**
     * セッション状態をクリア
     */
    clearSession() {
        try {
            this.backend.removeItem('pomodoro_session');
        } catch (e) {
            console.error('Failed to clear session:', e);
        }
    }

    /**
     * 設定を保存
     */
    saveConfig(config) {
        try {
            this.backend.setItem('pomodoro_config', JSON.stringify(config));
        } catch (e) {
            console.error('Failed to save config:', e);
        }
    }

    /**
     * 設定を復元
     */
    restoreConfig() {
        try {
            const stored = this.backend.getItem('pomodoro_config');
            return stored ? JSON.parse(stored) : null;
        } catch (e) {
            console.error('Failed to restore config:', e);
            return null;
        }
    }
}

// グローバルインスタンス
const appStorage = new AppStorage();

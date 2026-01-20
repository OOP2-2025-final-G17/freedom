"""
ユーザー設定の管理モジュール
通勤・通学時間、時給などの設定をJSON形式で管理します
"""

import os
import json
from typing import Dict, Any


class SettingsManager:
    """ユーザー設定を管理するクラス"""

    DEFAULT_SETTINGS = {
        "commute_time": 30,  # 通勤時間（分）
        "school_time": 60,  # 通学時間（分）
        "hourly_wage": 1000,  # 時給（円）
        "night_rate": 1.25,  # 深夜割増率（倍）
        "night_start": 22,  # 深夜開始時刻（時間）
        "night_end": 5,  # 深夜終了時刻（時間）
    }

    def __init__(self):
        """初期化"""
        self.settings_file = self._get_settings_file_path()
        self.settings = self._load_settings()

    @staticmethod
    def _get_settings_file_path() -> str:
        """設定ファイルのパスを取得"""
        # front_end/utils/settings_manager.py の位置から計算
        # utils -> front_end -> プロジェクトルート
        current_dir = os.path.dirname(os.path.abspath(__file__))  # utils のディレクトリ
        frontend_dir = os.path.dirname(current_dir)  # front_end のディレクトリ
        base_dir = os.path.dirname(frontend_dir)  # プロジェクトルート
        return os.path.join(base_dir, "json", "settings.json")

    def _load_settings(self) -> Dict[str, Any]:
        """設定ファイルから設定を読み込む"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                # ファイル読み込み失敗時はデフォルト設定を使用
                return self.DEFAULT_SETTINGS.copy()
        return self.DEFAULT_SETTINGS.copy()

    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """設定をファイルに保存"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.settings = settings
            return True
        except Exception:
            return False

    def get_setting(self, key: str) -> Any:
        """特定の設定値を取得"""
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def set_setting(self, key: str, value: Any) -> bool:
        """特定の設定値を更新"""
        self.settings[key] = value
        return self.save_settings(self.settings)

    def get_all_settings(self) -> Dict[str, Any]:
        """すべての設定値を取得"""
        return self.settings.copy()

    def reset_to_default(self) -> bool:
        """デフォルト設定にリセット"""
        return self.save_settings(self.DEFAULT_SETTINGS.copy())

    def validate_settings(self, settings: Dict[str, Any]) -> tuple[bool, str]:
        """設定値のバリデーション"""
        try:
            # 通勤時間の検証
            commute_time = int(settings.get("commute_time", 0))
            if commute_time < 0 or commute_time > 1440:
                return False, "通勤時間は0-1440分の範囲で設定してください。"

            # 通学時間の検証
            school_time = int(settings.get("school_time", 0))
            if school_time < 0 or school_time > 1440:
                return False, "通学時間は0-1440分の範囲で設定してください。"

            # 時給の検証
            hourly_wage = int(settings.get("hourly_wage", 0))
            if hourly_wage < 0 or hourly_wage > 100000:
                return False, "時給は0-100000円の範囲で設定してください。"

            # 深夜割増率の検証
            night_rate = float(settings.get("night_rate", 1.0))
            if night_rate < 1.0 or night_rate > 3.0:
                return False, "深夜割増率は1.0-3.0倍の範囲で設定してください。"

            # 深夜開始時刻の検証
            night_start = int(settings.get("night_start", 0))
            if night_start < 0 or night_start > 23:
                return False, "深夜開始時刻は0-23時の範囲で設定してください。"

            # 深夜終了時刻の検証
            night_end = int(settings.get("night_end", 0))
            if night_end < 0 or night_end > 23:
                return False, "深夜終了時刻は0-23時の範囲で設定してください。"

            return True, ""
        except (ValueError, TypeError):
            return False, "設定値が不正です。数値を入力してください。"


# グローバルインスタンス
_settings_manager = None


def get_settings_manager() -> SettingsManager:
    """SettingsManagerのシングルトンインスタンスを取得"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

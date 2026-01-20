"""
設定管理機能のテスト
front_end/utils/settings_manager.py の SettingsManager クラスをテストします
"""

import os
import sys
import json
import unittest
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from front_end.utils.settings_manager import SettingsManager, get_settings_manager


class SettingsManagerTestCase(unittest.TestCase):
    """SettingsManager のテストケース"""

    def setUp(self):
        """各テストの前に設定"""
        # 一時ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.temp_settings_file = os.path.join(self.temp_dir, "settings.json")

    def tearDown(self):
        """各テストの後にクリーンアップ"""
        # 一時ファイルを削除
        if os.path.exists(self.temp_settings_file):
            os.remove(self.temp_settings_file)
        os.rmdir(self.temp_dir)

    def test_default_settings(self):
        """デフォルト設定の取得"""
        self.assertIn("commute_time", SettingsManager.DEFAULT_SETTINGS)
        self.assertIn("school_time", SettingsManager.DEFAULT_SETTINGS)
        self.assertIn("hourly_wage", SettingsManager.DEFAULT_SETTINGS)
        self.assertIn("night_rate", SettingsManager.DEFAULT_SETTINGS)
        self.assertIn("night_start", SettingsManager.DEFAULT_SETTINGS)
        self.assertIn("night_end", SettingsManager.DEFAULT_SETTINGS)

    def test_load_settings_from_file(self):
        """ファイルから設定を読み込む"""
        mgr = SettingsManager()
        settings = mgr.get_all_settings()

        self.assertIsInstance(settings, dict)
        self.assertGreater(len(settings), 0)

    def test_get_setting(self):
        """特定の設定値を取得"""
        mgr = SettingsManager()

        commute_time = mgr.get_setting("commute_time")
        self.assertIsNotNone(commute_time)
        self.assertIsInstance(commute_time, int)

    def test_validate_settings_valid(self):
        """有効な設定のバリデーション"""
        mgr = SettingsManager()

        valid_settings = {
            "commute_time": 30,
            "school_time": 60,
            "hourly_wage": 1000,
            "night_rate": 1.25,
            "night_start": 22,
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(valid_settings)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_validate_settings_invalid_commute_time(self):
        """無効な通勤時間"""
        mgr = SettingsManager()

        invalid_settings = {
            "commute_time": 2000,  # 超過
            "school_time": 60,
            "hourly_wage": 1000,
            "night_rate": 1.25,
            "night_start": 22,
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(invalid_settings)
        self.assertFalse(is_valid)
        self.assertIn("通勤時間", msg)

    def test_validate_settings_invalid_hourly_wage(self):
        """無効な時給"""
        mgr = SettingsManager()

        invalid_settings = {
            "commute_time": 30,
            "school_time": 60,
            "hourly_wage": 200000,  # 超過
            "night_rate": 1.25,
            "night_start": 22,
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(invalid_settings)
        self.assertFalse(is_valid)
        self.assertIn("時給", msg)

    def test_validate_settings_invalid_night_rate(self):
        """無効な深夜割増率"""
        mgr = SettingsManager()

        invalid_settings = {
            "commute_time": 30,
            "school_time": 60,
            "hourly_wage": 1000,
            "night_rate": 5.0,  # 超過
            "night_start": 22,
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(invalid_settings)
        self.assertFalse(is_valid)
        self.assertIn("深夜割増率", msg)

    def test_validate_settings_invalid_night_time(self):
        """無効な深夜時刻"""
        mgr = SettingsManager()

        invalid_settings = {
            "commute_time": 30,
            "school_time": 60,
            "hourly_wage": 1000,
            "night_rate": 1.25,
            "night_start": 25,  # 無効
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(invalid_settings)
        self.assertFalse(is_valid)
        self.assertIn("深夜開始時刻", msg)

    def test_validate_settings_non_numeric(self):
        """非数値の設定"""
        mgr = SettingsManager()

        invalid_settings = {
            "commute_time": "abc",  # 文字列
            "school_time": 60,
            "hourly_wage": 1000,
            "night_rate": 1.25,
            "night_start": 22,
            "night_end": 5,
        }

        is_valid, msg = mgr.validate_settings(invalid_settings)
        self.assertFalse(is_valid)

    def test_get_all_settings(self):
        """すべての設定を取得"""
        mgr = SettingsManager()
        settings = mgr.get_all_settings()

        required_keys = [
            "commute_time",
            "school_time",
            "hourly_wage",
            "night_rate",
            "night_start",
            "night_end",
        ]
        for key in required_keys:
            self.assertIn(key, settings)

    def test_settings_file_exists(self):
        """設定ファイルが存在することを確認"""
        mgr = SettingsManager()
        self.assertTrue(os.path.exists(mgr.settings_file))

    def test_settings_json_format(self):
        """設定ファイルがJSON形式であることを確認"""
        mgr = SettingsManager()
        with open(mgr.settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_singleton_instance(self):
        """シングルトンパターンの確認"""
        mgr1 = get_settings_manager()
        mgr2 = get_settings_manager()
        self.assertIs(mgr1, mgr2)


if __name__ == "__main__":
    unittest.main()

"""
バリデーション関数のテスト
front_end/utils/validators.py の検証関数をテストします
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from front_end.utils.validators import validate_schedule_format


class ValidatorsTestCase(unittest.TestCase):
    """バリデーション関数のテストケース"""

    def test_valid_schedule_format(self):
        """正常なスケジュール入力"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="10:30",
        )
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_empty_name(self):
        """空のタイトル"""
        is_valid, msg = validate_schedule_format(
            name="",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="10:30",
        )
        self.assertFalse(is_valid)
        self.assertIn("タイトル", msg)

    def test_invalid_start_date_format(self):
        """無効な開始日フォーマット"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026/01/08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="10:30",
        )
        self.assertFalse(is_valid)
        self.assertIn("日付", msg)

    def test_invalid_start_time_format(self):
        """無効な開始時刻フォーマット"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="25:00",  # 無効な時刻
            end_date_str="2026-01-08",
            end_time_str="10:30",
        )
        self.assertFalse(is_valid)
        self.assertIn("時刻", msg)

    def test_invalid_end_date_format(self):
        """無効な終了日フォーマット"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-13-01",  # 無効な月
            end_time_str="10:30",
        )
        self.assertFalse(is_valid)
        self.assertIn("日付", msg)

    def test_invalid_end_time_format(self):
        """無効な終了時刻フォーマット"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="10:61",  # 無効な分
        )
        self.assertFalse(is_valid)
        self.assertIn("時刻", msg)

    def test_end_before_start(self):
        """終了時刻が開始時刻より前"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="10:00",
            end_date_str="2026-01-08",
            end_time_str="09:00",
        )
        self.assertFalse(is_valid)
        self.assertIn("終了", msg)

    def test_same_start_and_end(self):
        """開始時刻と終了時刻が同じ"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="09:00",
        )
        self.assertFalse(is_valid)

    def test_valid_mode_values(self):
        """モードの検証（A, B, NULL）"""
        for mode in ["A", "B", "NULL"]:
            is_valid, msg = validate_schedule_format(
                name="スケジュール",
                mode=mode,
                start_date_str="2026-01-08",
                start_time_str="09:00",
                end_date_str="2026-01-08",
                end_time_str="10:30",
            )
            self.assertTrue(is_valid, f"モード {mode} が無効です")

    def test_multiday_schedule(self):
        """複数日にまたがるスケジュール"""
        is_valid, msg = validate_schedule_format(
            name="講義A",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-09",
            end_time_str="10:30",
        )
        self.assertTrue(is_valid)

    def test_whitespace_in_name(self):
        """名前にホワイトスペースが含まれている"""
        is_valid, msg = validate_schedule_format(
            name="  講義A  ",
            mode="A",
            start_date_str="2026-01-08",
            start_time_str="09:00",
            end_date_str="2026-01-08",
            end_time_str="10:30",
        )
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()

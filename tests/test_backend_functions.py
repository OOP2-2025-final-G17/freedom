"""
バックエンド関数のユニットテスト
back_end/functions.py の各関数をテストします
"""

import os
import sys
import unittest
from datetime import date, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from back_end.functions import (
    add_schedule,
    get_schedule,
    delete_schedule,
    update_schedule,
    get_monthly_schedule,
    schedule_to_dict,
)
from back_end.db.db import db, Schedule


class BackendFunctionsTestCase(unittest.TestCase):
    """バックエンド関数のテストケース"""

    @classmethod
    def setUpClass(cls):
        """テスト実行前にデータベース接続と初期化"""
        db.connect(reuse_if_open=True)
        db.create_tables([Schedule], safe=True)

    def setUp(self):
        """各テストの前にテーブルを空にする"""
        db.connect(reuse_if_open=True)
        # テーブル内のすべてのレコードを削除
        Schedule.delete().execute()

    def tearDown(self):
        """各テストの後にクリーンアップ"""
        Schedule.delete().execute()

    def test_add_schedule_success(self):
        """スケジュール追加の成功ケース"""
        payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        result = add_schedule(payload)

        self.assertTrue(result.get("ok"))
        self.assertEqual(result.get("action"), "add_schedule")
        data = result.get("data", {})
        self.assertIn("schedule", data)
        schedule = data["schedule"]
        self.assertEqual(schedule.get("name"), "講義A")
        self.assertEqual(schedule.get("mode"), "A")

    def test_add_schedule_invalid_date_format(self):
        """無効な日付フォーマット"""
        payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026/01/08",  # 無効なフォーマット
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        result = add_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "BAD_REQUEST")

    def test_add_schedule_end_before_start(self):
        """終了時刻が開始時刻より前のケース"""
        payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "10:00",
            "end_date": "2026-01-08",
            "end_time": "09:00",  # 開始時刻より前
        }
        result = add_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "VALIDATION_ERROR")

    def test_get_schedule_success(self):
        """スケジュール取得の成功ケース"""
        # 先にスケジュールを追加
        add_payload = {
            "mode": "B",
            "name": "バイト",
            "start_date": "2026-01-08",
            "start_time": "14:00",
            "end_date": "2026-01-08",
            "end_time": "18:00",
        }
        add_schedule(add_payload)

        # 指定日のスケジュールを取得
        get_payload = {"date": "2026-01-08"}
        result = get_schedule(get_payload)

        self.assertTrue(result.get("ok"))
        data = result.get("data", {})
        schedules = data.get("schedules", [])
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].get("name"), "バイト")

    def test_get_schedule_no_date_param(self):
        """dateパラメータなしでのリクエスト"""
        payload = {}
        result = get_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "BAD_REQUEST")

    def test_get_schedule_empty_result(self):
        """該当する予定がない場合"""
        payload = {"date": "2026-12-25"}
        result = get_schedule(payload)

        self.assertTrue(result.get("ok"))
        data = result.get("data", {})
        schedules = data.get("schedules", [])
        self.assertEqual(len(schedules), 0)

    def test_update_schedule_success(self):
        """スケジュール更新の成功ケース"""
        # 先にスケジュールを追加
        add_payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        add_result = add_schedule(add_payload)
        schedule_id = add_result.get("data", {}).get("schedule", {}).get("id")

        # スケジュールを更新
        update_payload = {
            "id": schedule_id,
            "mode": "B",
            "name": "バイト",
            "start_date": "2026-01-09",
            "start_time": "14:00",
            "end_date": "2026-01-09",
            "end_time": "18:00",
        }
        update_result = update_schedule(update_payload)

        self.assertTrue(update_result.get("ok"))
        updated = update_result.get("data", {}).get("schedule", {})
        self.assertEqual(updated.get("name"), "バイト")
        self.assertEqual(updated.get("mode"), "B")
        self.assertEqual(updated.get("start_date"), "2026-01-09")

    def test_update_schedule_not_found(self):
        """存在しないIDでの更新"""
        payload = {
            "id": 9999,
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        result = update_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "NOT_FOUND")

    def test_delete_schedule_success(self):
        """スケジュール削除の成功ケース"""
        # 先にスケジュールを追加
        add_payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        add_result = add_schedule(add_payload)
        schedule_id = add_result.get("data", {}).get("schedule", {}).get("id")

        # スケジュールを削除
        delete_payload = {"id": schedule_id}
        delete_result = delete_schedule(delete_payload)

        self.assertTrue(delete_result.get("ok"))
        self.assertEqual(delete_result.get("data", {}).get("deleted"), schedule_id)

        # 削除されたことを確認
        check_result = get_schedule({"date": "2026-01-08"})
        self.assertEqual(len(check_result.get("data", {}).get("schedules", [])), 0)

    def test_delete_schedule_no_id(self):
        """IDなしでの削除リクエスト"""
        payload = {}
        result = delete_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "BAD_REQUEST")

    def test_delete_schedule_not_found(self):
        """存在しないIDでの削除"""
        payload = {"id": 9999}
        result = delete_schedule(payload)

        self.assertFalse(result.get("ok"))
        error = result.get("error", {})
        self.assertEqual(error.get("code"), "NOT_FOUND")

    def test_get_monthly_schedule(self):
        """月全体のスケジュール取得"""
        # 複数のスケジュールを追加
        schedules_data = [
            {
                "mode": "A",
                "name": "講義A",
                "start_date": "2026-01-08",
                "start_time": "09:00",
                "end_date": "2026-01-08",
                "end_time": "10:30",
            },
            {
                "mode": "B",
                "name": "バイト",
                "start_date": "2026-01-15",
                "start_time": "14:00",
                "end_date": "2026-01-15",
                "end_time": "18:00",
            },
        ]
        for payload in schedules_data:
            add_schedule(payload)

        # 月全体を取得
        get_payload = {"year": 2026, "month": 1}
        result = get_monthly_schedule(get_payload)

        self.assertTrue(result.get("ok"))
        data = result.get("data", {})
        schedules = data.get("schedules", [])
        self.assertEqual(len(schedules), 2)

    def test_schedule_to_dict_conversion(self):
        """Schedule モデルをディクショナリに変換"""
        # スケジュールを追加してから取得
        add_payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        add_schedule(add_payload)

        # データベースから直接取得
        schedule = Schedule.select().first()
        dict_result = schedule_to_dict(schedule)

        self.assertIsInstance(dict_result, dict)
        self.assertEqual(dict_result.get("name"), "講義A")
        self.assertEqual(dict_result.get("start_date"), "2026-01-08")
        self.assertEqual(dict_result.get("start_time"), "09:00")
        self.assertIn("id", dict_result)


if __name__ == "__main__":
    unittest.main()

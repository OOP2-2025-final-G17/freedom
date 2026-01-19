"""
統合テスト
リクエスト処理からレスポンスまでの一連の流れをテストします
"""

import os
import sys
import json
import unittest
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from back_end.functions import (
    add_schedule,
    get_schedule,
    delete_schedule,
    update_schedule,
)
from back_end.db.db import db, Schedule


class IntegrationTestCase(unittest.TestCase):
    """統合テストケース"""

    @classmethod
    def setUpClass(cls):
        """テスト実行前にデータベース接続と初期化"""
        db.connect(reuse_if_open=True)
        db.create_tables([Schedule], safe=True)

    def setUp(self):
        """各テストの前にテーブルを空にする"""
        db.connect(reuse_if_open=True)
        Schedule.delete().execute()

    def tearDown(self):
        """各テストの後にクリーンアップ"""
        Schedule.delete().execute()

    def test_full_schedule_lifecycle(self):
        """スケジュールのライフサイクル全体をテスト（追加→取得→更新→削除）"""
        # 1. スケジュール追加
        add_payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-08",
            "end_time": "10:30",
        }
        add_result = add_schedule(add_payload)
        self.assertTrue(add_result.get("ok"))
        schedule_id = add_result.get("data", {}).get("schedule", {}).get("id")
        self.assertIsNotNone(schedule_id)

        # 2. スケジュール取得
        get_result = get_schedule({"date": "2026-01-08"})
        self.assertTrue(get_result.get("ok"))
        schedules = get_result.get("data", {}).get("schedules", [])
        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0].get("id"), schedule_id)

        # 3. スケジュール更新
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

        # 4. スケジュール削除
        delete_result = delete_schedule({"id": schedule_id})
        self.assertTrue(delete_result.get("ok"))

        # 5. 削除の確認
        final_result = get_schedule({"date": "2026-01-09"})
        self.assertEqual(len(final_result.get("data", {}).get("schedules", [])), 0)

    def test_multiple_schedules_same_day(self):
        """同一日付に複数のスケジュールが存在するケース"""
        payloads = [
            {
                "mode": "A",
                "name": "講義A",
                "start_date": "2026-01-08",
                "start_time": "09:00",
                "end_date": "2026-01-08",
                "end_time": "10:30",
            },
            {
                "mode": "A",
                "name": "講義B",
                "start_date": "2026-01-08",
                "start_time": "11:00",
                "end_date": "2026-01-08",
                "end_time": "12:30",
            },
            {
                "mode": "B",
                "name": "バイト",
                "start_date": "2026-01-08",
                "start_time": "14:00",
                "end_date": "2026-01-08",
                "end_time": "18:00",
            },
        ]

        # すべてのスケジュールを追加
        for payload in payloads:
            result = add_schedule(payload)
            self.assertTrue(result.get("ok"))

        # 指定日のスケジュールを取得
        get_result = get_schedule({"date": "2026-01-08"})
        schedules = get_result.get("data", {}).get("schedules", [])

        # 3つのスケジュールが取得される
        self.assertEqual(len(schedules), 3)

        # 時刻順に並んでいることを確認
        for i in range(len(schedules) - 1):
            current_time = schedules[i].get("start_time")
            next_time = schedules[i + 1].get("start_time")
            self.assertLess(current_time, next_time)

    def test_overlapping_schedules(self):
        """重複するスケジュール"""
        payloads = [
            {
                "mode": "A",
                "name": "講義A",
                "start_date": "2026-01-08",
                "start_time": "09:00",
                "end_date": "2026-01-08",
                "end_time": "11:00",
            },
            {
                "mode": "B",
                "name": "バイト",
                "start_date": "2026-01-08",
                "start_time": "10:00",
                "end_date": "2026-01-08",
                "end_time": "14:00",
            },
        ]

        # 両方のスケジュールを追加（重複を許容）
        for payload in payloads:
            result = add_schedule(payload)
            self.assertTrue(result.get("ok"))

        # 指定日のスケジュールを取得
        get_result = get_schedule({"date": "2026-01-08"})
        schedules = get_result.get("data", {}).get("schedules", [])

        self.assertEqual(len(schedules), 2)

    def test_multiday_schedule_retrieval(self):
        """複数日スケジュールの取得テスト"""
        payload = {
            "mode": "A",
            "name": "講義A",
            "start_date": "2026-01-08",
            "start_time": "09:00",
            "end_date": "2026-01-10",
            "end_time": "18:00",
        }
        add_result = add_schedule(payload)
        self.assertTrue(add_result.get("ok"))

        # 3日間のどれでも取得できるか確認
        for day in ["2026-01-08", "2026-01-09", "2026-01-10"]:
            get_result = get_schedule({"date": day})
            schedules = get_result.get("data", {}).get("schedules", [])
            self.assertEqual(len(schedules), 1)
            self.assertEqual(schedules[0].get("name"), "講義A")

    def test_edge_case_midnight_schedule(self):
        """深夜のスケジュール（終了時刻が翌日）"""
        payload = {
            "mode": "B",
            "name": "夜勤",
            "start_date": "2026-01-08",
            "start_time": "22:00",
            "end_date": "2026-01-09",
            "end_time": "06:00",
        }
        add_result = add_schedule(payload)
        self.assertTrue(add_result.get("ok"))

        # 両日で取得できるか確認
        result_8 = get_schedule({"date": "2026-01-08"})
        result_9 = get_schedule({"date": "2026-01-09"})

        self.assertEqual(len(result_8.get("data", {}).get("schedules", [])), 1)
        self.assertEqual(len(result_9.get("data", {}).get("schedules", [])), 1)


if __name__ == "__main__":
    unittest.main()

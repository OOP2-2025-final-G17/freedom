"""
フロントエンド UI テスト
UIコンポーネントとユーザーインタラクションをテストします
"""

import os
import sys
import json
import unittest
import tkinter as tk
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

JSON_DIR = os.path.join(ROOT, "json")
REQ_PATH = os.path.join(JSON_DIR, "request.json")
RES_PATH = os.path.join(JSON_DIR, "response.json")


class UITestCase(unittest.TestCase):
    """UI テストの基底クラス"""

    def setUp(self):
        """各テストの前にセットアップ"""
        os.makedirs(JSON_DIR, exist_ok=True)

        # バックアップ
        self._req_backup = None
        self._res_backup = None
        if os.path.exists(REQ_PATH):
            with open(REQ_PATH, "r", encoding="utf-8") as f:
                self._req_backup = f.read()
        if os.path.exists(RES_PATH):
            with open(RES_PATH, "r", encoding="utf-8") as f:
                self._res_backup = f.read()

        # Tk root
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """各テストの後にクリーンアップ"""
        try:
            for w in list(self.root.winfo_children()):
                try:
                    w.destroy()
                except Exception:
                    pass
            self.root.destroy()
        except Exception:
            pass

        # リストア
        if self._req_backup is None:
            if os.path.exists(REQ_PATH):
                os.remove(REQ_PATH)
        else:
            with open(REQ_PATH, "w", encoding="utf-8") as f:
                f.write(self._req_backup)

        if self._res_backup is None:
            if os.path.exists(RES_PATH):
                os.remove(RES_PATH)
        else:
            with open(RES_PATH, "w", encoding="utf-8") as f:
                f.write(self._res_backup)

    def _read_json(self, path):
        """JSON ファイルを読み込む"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


class TestCalendarWindow(UITestCase):
    """カレンダーウィンドウのテスト"""

    def test_calendar_initialization(self):
        """カレンダーの初期化"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        today = dt.date.today()

        # 初期状態の確認
        self.assertEqual(cw.year.get(), today.year)
        self.assertEqual(cw.month.get(), today.month)
        self.assertIsNone(cw.selected_date)

    def test_calendar_month_navigation(self):
        """月のナビゲーション"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        y0, m0 = cw.year.get(), cw.month.get()

        # 前月へ
        cw.prev_month()
        y1, m1 = cw.year.get(), cw.month.get()
        self.assertNotEqual((y0, m0), (y1, m1))

        # 翌月へ
        cw.next_month()
        y2, m2 = cw.year.get(), cw.month.get()
        self.assertEqual((y0, m0), (y2, m2))

    def test_calendar_go_to_today(self):
        """今日に戻る"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        today = dt.date.today()

        # 月を変更
        cw.prev_month()
        self.assertNotEqual(cw.month.get(), today.month)

        # 今日に戻す
        cw.go_to_today()
        self.assertEqual(cw.year.get(), today.year)
        self.assertEqual(cw.month.get(), today.month)

    def test_calendar_date_selection(self):
        """日付選択"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        target_date = dt.date(2026, 1, 8)

        cw.select_date(target_date)

        # 選択状態を確認
        self.assertEqual(cw.selected_date, target_date)
        self.assertIn(target_date.isoformat(), cw.sel_var.get())

    def test_calendar_request_day(self):
        """日付の予定取得リクエスト"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        target_date = dt.date(2026, 1, 8)

        cw.select_date(target_date)
        cw.request_day()

        # リクエストが生成されたことを確認
        self.assertTrue(os.path.exists(REQ_PATH))
        data = self._read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "get_schedule")
        self.assertEqual(data.get("date"), target_date.isoformat())

    def test_calendar_request_month(self):
        """月の予定取得リクエスト"""
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        y, m = 2026, 1
        cw.year.set(y)
        cw.month.set(m)

        cw.request_month()

        # リクエストが生成されたことを確認
        self.assertTrue(os.path.exists(REQ_PATH))
        data = self._read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "get_monthly_schedule")
        self.assertEqual(data.get("year"), y)
        self.assertEqual(data.get("month"), m)


class TestChangeWindow(UITestCase):
    """変更ウィンドウのテスト"""

    def test_change_window_initialization(self):
        """変更ウィンドウの初期化"""
        import front_end.change as change_mod

        change_mod.messagebox.showinfo = lambda *a, **k: None

        from front_end.change import ChangeWindow

        ch = ChangeWindow(self.root)

        # デフォルト値の確認
        self.assertEqual(ch.mode_var.get(), "A")
        today = dt.date.today()
        self.assertIn(today.isoformat(), ch.start_date.get())

    def test_change_window_existing_schedule(self):
        """既存スケジュールでのウィンドウ初期化"""
        import front_end.change as change_mod

        change_mod.messagebox.showinfo = lambda *a, **k: None

        from front_end.change import ChangeWindow

        existing = {
            "id": 1,
            "mode": "B",
            "name": "バイト",
            "start_date": "2026-01-08",
            "start_time": "14:00",
            "end_date": "2026-01-08",
            "end_time": "18:00",
        }

        ch = ChangeWindow(self.root, existing_schedule=existing)

        # 既存値が反映されているか確認
        self.assertEqual(ch.mode_var.get(), "B")
        self.assertIn("バイト", ch.name_entry.get())

    def test_change_window_add_schedule(self):
        """新規スケジュール追加"""
        import front_end.change as change_mod

        change_mod.messagebox.showinfo = lambda *a, **k: None
        change_mod.messagebox.showwarning = lambda *a, **k: None

        from front_end.change import ChangeWindow

        ch = ChangeWindow(self.root)

        # 入力を設定
        ch.mode_var.set("A")
        ch.name_entry.delete(0, "end")
        ch.name_entry.insert(0, "講義A")
        ch.start_date.delete(0, "end")
        ch.start_date.insert(0, "2026-01-08")
        ch.start_time.delete(0, "end")
        ch.start_time.insert(0, "09:00")
        ch.end_date.delete(0, "end")
        ch.end_date.insert(0, "2026-01-08")
        ch.end_time.delete(0, "end")
        ch.end_time.insert(0, "10:30")

        ch.submit()

        # リクエストが生成されたことを確認
        self.assertTrue(os.path.exists(REQ_PATH))
        data = self._read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "add_schedule")
        self.assertEqual(data.get("mode"), "A")
        self.assertEqual(data.get("name"), "講義A")

    def test_change_window_validation_error(self):
        """バリデーションエラーのテスト"""
        import front_end.change as change_mod

        error_shown = []
        change_mod.messagebox.showwarning = lambda title, msg, **k: error_shown.append(
            msg
        )

        from front_end.change import ChangeWindow

        ch = ChangeWindow(self.root)

        # 無効な入力：終了時刻が開始時刻より前
        ch.mode_var.set("A")
        ch.name_entry.delete(0, "end")
        ch.name_entry.insert(0, "講義A")
        ch.start_date.delete(0, "end")
        ch.start_date.insert(0, "2026-01-08")
        ch.start_time.delete(0, "end")
        ch.start_time.insert(0, "10:00")
        ch.end_date.delete(0, "end")
        ch.end_date.insert(0, "2026-01-08")
        ch.end_time.delete(0, "end")
        ch.end_time.insert(0, "09:00")

        ch.submit()

        # エラーが表示されたことを確認
        self.assertTrue(len(error_shown) > 0)


class TestMainMenu(UITestCase):
    """メインメニューのテスト"""

    def test_menu_initialization(self):
        """メニューの初期化"""
        from front_end.menu import MainMenu

        menu = MainMenu(self.root)

        # ボタンが存在するか確認
        self.assertTrue(hasattr(menu, "btn_change"))
        self.assertTrue(hasattr(menu, "btn_salary"))
        self.assertTrue(hasattr(menu, "btn_export"))
        self.assertTrue(hasattr(menu, "btn_import"))

    def test_menu_open_change(self):
        """メニューから変更ウィンドウを開く"""
        import front_end.change as change_mod

        change_mod.messagebox.showinfo = lambda *a, **k: None

        from front_end.menu import MainMenu

        menu = MainMenu(self.root)
        initial_status = menu.status_var.get()

        menu.open_change()

        # ステータスが更新されたか確認
        self.assertIn("予定の追加/変更", menu.status_var.get())
        self.assertNotEqual(initial_status, menu.status_var.get())

    def test_menu_open_salary(self):
        """メニューから給料計算を開く"""
        import front_end.salary as salary_mod

        salary_mod.messagebox.showinfo = lambda *a, **k: None

        from front_end.menu import MainMenu

        menu = MainMenu(self.root)

        menu.open_salary()

        # ステータスが更新されたか確認
        self.assertIn("給料計算", menu.status_var.get())


if __name__ == "__main__":
    unittest.main()

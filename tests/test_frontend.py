import os
import sys
import json
import unittest
import tkinter as tk
import datetime as dt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# テストをスクリプト実行した場合でもルートを import パスに追加
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
JSON_DIR = os.path.join(ROOT, "json")
REQ_PATH = os.path.join(JSON_DIR, "request.json")
RES_PATH = os.path.join(JSON_DIR, "response.json")


class FrontendTestCase(unittest.TestCase):
    def setUp(self):
        os.makedirs(JSON_DIR, exist_ok=True)
        # バックアップ既存ファイル
        self._req_backup = None
        self._res_backup = None
        if os.path.exists(REQ_PATH):
            with open(REQ_PATH, "r", encoding="utf-8") as f:
                self._req_backup = f.read()
        if os.path.exists(RES_PATH):
            with open(RES_PATH, "r", encoding="utf-8") as f:
                self._res_backup = f.read()

        # Tk root を用意（非表示）
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        # 生成したウィンドウやrootを閉じる
        try:
            self.root.destroy()
        except Exception:
            pass

        # request/response を元に戻す
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
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_menu_buttons_open(self):
        from front_end.menu import MainMenu

        menu = MainMenu(self.root)
        # 各ボタンのコールバック呼び出し（ウィンドウ生成）
        menu.open_change()
        # ステータス文言が更新されているか
        self.assertIn("モード", menu.status_var.get())

    def test_calendar_request(self):
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        # 日付選択→リクエスト
        target = dt.date(2026, 1, 8)
        cw.select_date(target)
        cw.request_day()

        self.assertTrue(os.path.exists(REQ_PATH))
        data = self._read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "get_schedule")
        self.assertEqual(data.get("date"), target.isoformat())

    def test_change_submit(self):
        import front_end.change as change_mod

        # GUIダイアログが出ないようにモック
        change_mod.messagebox.showinfo = lambda *a, **k: None
        change_mod.messagebox.showwarning = lambda *a, **k: None
        ChangeWindow = change_mod.ChangeWindow

        ch = ChangeWindow(self.root)
        # 入力値設定
        ch.mode_var.set("A")
        ch.name_entry.insert(0, "講義A")
        ch.start_date.delete(0, "end")
        ch.start_date.insert(0, "2026-01-08")
        ch.start_time.delete(0, "end")
        ch.start_time.insert(0, "09:00")
        ch.end_date.delete(0, "end")
        ch.end_date.insert(0, "2026-01-08")
        ch.end_time.delete(0, "end")
        ch.end_time.insert(0, "10:30")

        # 送信
        ch.submit()

        self.assertTrue(os.path.exists(REQ_PATH))
        data = self._read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "save_schedule")
        self.assertEqual(data.get("mode"), "A")
        self.assertEqual(data.get("name"), "講義A")
        self.assertEqual(data.get("start_date"), "2026-01-08")
        self.assertEqual(data.get("start_time"), "09:00")
        self.assertEqual(data.get("end_date"), "2026-01-08")
        self.assertEqual(data.get("end_time"), "10:30")


if __name__ == "__main__":
    unittest.main()

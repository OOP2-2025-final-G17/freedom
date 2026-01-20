import os
import sys
import json
import unittest
import tkinter as tk
import datetime as dt


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(ROOT, "json")
REQ_PATH = os.path.join(JSON_DIR, "request.json")
RES_PATH = os.path.join(JSON_DIR, "response.json")

# プロジェクトルートを import パスに追加
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


class TkTestCase(unittest.TestCase):
    def setUp(self):
        os.makedirs(JSON_DIR, exist_ok=True)
        # 既存ファイルのバックアップ
        self._req_backup = None
        self._res_backup = None
        if os.path.exists(REQ_PATH):
            with open(REQ_PATH, "r", encoding="utf-8") as f:
                self._req_backup = f.read()
        if os.path.exists(RES_PATH):
            with open(RES_PATH, "r", encoding="utf-8") as f:
                self._res_backup = f.read()

        # Tk root（非表示）
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            # 子ウィンドウを含めて閉じる
            for w in list(self.root.winfo_children()):
                try:
                    w.destroy()
                except Exception:
                    pass
            self.root.destroy()
        except Exception:
            pass

        # request/response を復元
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

    def read_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


class TestMainImport(TkTestCase):
    def test_main_import(self):
        import main

        self.assertTrue(hasattr(main, "run_app"))


class TestCalendar(TkTestCase):
    def test_navigation_and_selection(self):
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        y0, m0 = cw.year.get(), cw.month.get()
        cw.prev_month()
        y1, m1 = cw.year.get(), cw.month.get()
        cw.next_month()
        y2, m2 = cw.year.get(), cw.month.get()

        # 前月/翌月が機能していること
        self.assertNotEqual((y0, m0), (y1, m1))
        self.assertEqual((y0, m0), (y2, m2))

        # 選択反映
        d = dt.date(y0, m0, 1)
        cw.select_date(d)
        self.assertEqual(cw.selected_date, d)
        self.assertIn(d.isoformat(), cw.sel_var.get())

    def test_request_for_selected_day(self):
        from front_end.calender import CalendarWindow

        cw = CalendarWindow(self.root)
        target = dt.date(2026, 1, 8)
        cw.select_date(target)
        cw.request_day()

        self.assertTrue(os.path.exists(REQ_PATH))
        data = self.read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "get_schedule")
        self.assertEqual(data.get("date"), target.isoformat())

    def test_request_without_selection_shows_info(self):
        import front_end.calender as cal_mod

        # ダイアログをモック
        called = {"info": 0}

        def _info(*args, **kwargs):
            called["info"] += 1

        cal_mod.messagebox.showinfo = _info

        CalendarWindow = cal_mod.CalendarWindow
        cw = CalendarWindow(self.root)
        cw.selected_date = None
        cw.request_day()
        self.assertEqual(called["info"], 1)
        # request.json は生成される（選択日がなくても警告後にリクエストは送信される可能性がある）
        # または、選択なしの場合はリクエストを送らないようにする必要がある


class TestChange(TkTestCase):
    def test_submit_validation(self):
        import front_end.change as change_mod

        called = {"warn": 0}
        change_mod.messagebox.showwarning = lambda *a, **k: called.__setitem__(
            "warn", called["warn"] + 1
        )
        ChangeWindow = change_mod.ChangeWindow

        # 検証開始前に既存の request.json があれば削除
        if os.path.exists(REQ_PATH):
            os.remove(REQ_PATH)

        ch = ChangeWindow(self.root)
        # name未入力のまま送信
        ch.submit()
        self.assertEqual(called["warn"], 1)
        self.assertFalse(os.path.exists(REQ_PATH))

    def test_submit_modes_and_payload(self):
        import front_end.change as change_mod

        # ダイアログ抑制
        change_mod.messagebox.showinfo = lambda *a, **k: None
        ChangeWindow = change_mod.ChangeWindow

        ch = ChangeWindow(self.root)
        ch.mode_var.set("B")
        ch.name_entry.insert(0, "バイト")
        ch.start_date.delete(0, "end")
        ch.start_date.insert(0, "2026-01-10")
        ch.start_time.delete(0, "end")
        ch.start_time.insert(0, "18:00")
        ch.end_date.delete(0, "end")
        ch.end_date.insert(0, "2026-01-10")
        ch.end_time.delete(0, "end")
        ch.end_time.insert(0, "22:00")
        ch.submit()

        self.assertTrue(os.path.exists(REQ_PATH))
        data = self.read_json(REQ_PATH)
        self.assertEqual(data.get("action"), "add_schedule")
        self.assertEqual(data.get("mode"), "B")
        self.assertEqual(data.get("name"), "バイト")


class TestMoney(TkTestCase):
    def test_invalid_month_warning(self):
        import front_end.money as money_mod

        called = {"warn": 0}

        def _warn(*args, **kwargs):
            called["warn"] += 1

        money_mod.messagebox.showwarning = _warn
        MoneyWindow = money_mod.MoneyWindow

        if os.path.exists(REQ_PATH):
            os.remove(REQ_PATH)

        mw = MoneyWindow(self.root)
        mw.month_var.set(13)
        mw.request_calc()
        self.assertEqual(called["warn"], 1)
        self.assertFalse(os.path.exists(REQ_PATH))

    def test_request_and_show_result(self):
        import front_end.money as money_mod

        # showinfoは抑制
        money_mod.messagebox.showinfo = lambda *a, **k: None
        MoneyWindow = money_mod.MoneyWindow

        mw = MoneyWindow(self.root)
        mw.year_var.set(2026)
        mw.month_var.set(1)
        mw.request_calc()

        self.assertTrue(os.path.exists(REQ_PATH))
        req = self.read_json(REQ_PATH)
        self.assertEqual(req.get("action"), "calc_wage")
        self.assertEqual(req.get("year"), 2026)
        self.assertEqual(req.get("month"), 1)

        resp = {
            "action": "calc_wage_result",
            "year": 2026,
            "month": 1,
            "total_hours": 7.5,
            "total_wage": 9000,
            "detail": [
                {"date": "2026-01-02", "hours": 3.0, "wage": 1200, "amount": 3600},
                {"date": "2026-01-03", "hours": 4.5, "wage": 1200, "amount": 5400},
            ],
        }
        with open(RES_PATH, "w", encoding="utf-8") as f:
            json.dump(resp, f, ensure_ascii=False, indent=2)

        mw.try_show_result()
        output = mw.output.get("1.0", "end").strip()
        self.assertIn("総労働時間: 7.5 時間", output)
        self.assertIn("推定給料: 9000 円", output)
        self.assertIn("2026-01-02", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)

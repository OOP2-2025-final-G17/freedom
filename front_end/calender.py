import os
import json
import datetime as dt
import calendar as pycal
import tkinter as tk
from tkinter import ttk, messagebox


def _paths():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req = os.path.join(base, "json", "request.json")
    res = os.path.join(base, "json", "response.json")
    return req, res


def write_request(payload: dict) -> None:
    req, _ = _paths()
    os.makedirs(os.path.dirname(req), exist_ok=True)
    with open(req, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def try_read_response() -> dict | None:
    _, res = _paths()
    if not os.path.exists(res):
        return None
    try:
        with open(res, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


class CalendarWindow(tk.Frame):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)

        today = dt.date.today()
        self.year = tk.IntVar(value=today.year)
        self.month = tk.IntVar(value=today.month)
        self.selected_date: dt.date | None = None

        control = ttk.Frame(self)
        control.pack(fill=tk.X, padx=10, pady=8)

        prev_btn = ttk.Button(control, text="<", width=3, command=self.prev_month)
        prev_btn.pack(side=tk.LEFT)

        self.title_var = tk.StringVar()
        title_lbl = ttk.Label(
            control, textvariable=self.title_var, font=("Helvetica", 14, "bold")
        )
        title_lbl.pack(side=tk.LEFT, expand=True)

        next_btn = ttk.Button(control, text=">", width=3, command=self.next_month)
        next_btn.pack(side=tk.RIGHT)

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=6)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=6)

        self.sel_var = tk.StringVar(value="日付未選択")
        ttk.Label(action_frame, textvariable=self.sel_var).pack(side=tk.LEFT)

        ttk.Button(
            action_frame, text="この日の予定を取得", command=self.request_day
        ).pack(side=tk.RIGHT)

        self.result = tk.Text(self, height=10)
        self.result.pack(fill=tk.BOTH, expand=False, padx=10, pady=6)

        self.draw_calendar()

    def draw_calendar(self) -> None:
        # 既存ウィジェット削除
        for w in self.grid_frame.winfo_children():
            w.destroy()

        y, m = self.year.get(), self.month.get()
        self.title_var.set(f"{y}年 {m}月")

        # 曜日ヘッダ
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        for i, wd in enumerate(weekdays):
            ttk.Label(self.grid_frame, text=wd, anchor="center").grid(
                row=0, column=i, sticky="nsew"
            )

        cal = pycal.Calendar(firstweekday=0)  # 0: Monday
        row = 1
        for week in cal.monthdatescalendar(y, m):
            for col, day in enumerate(week):
                is_current_month = day.month == m
                btn = ttk.Button(
                    self.grid_frame,
                    text=str(day.day),
                    width=4,
                    command=lambda d=day: self.select_date(d),
                )
                if not is_current_month:
                    btn.state(["disabled"])  # 当月以外は無効
                btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            row += 1

        # 均等拡張
        for r in range(row + 1):
            self.grid_frame.rowconfigure(r, weight=1)
        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)

    def select_date(self, day: dt.date) -> None:
        self.selected_date = day
        self.sel_var.set(f"選択: {day.isoformat()}")

    def prev_month(self) -> None:
        y, m = self.year.get(), self.month.get()
        if m == 1:
            self.year.set(y - 1)
            self.month.set(12)
        else:
            self.month.set(m - 1)
        self.draw_calendar()

    def next_month(self) -> None:
        y, m = self.year.get(), self.month.get()
        if m == 12:
            self.year.set(y + 1)
            self.month.set(1)
        else:
            self.month.set(m + 1)
        self.draw_calendar()

    def request_day(self) -> None:
        if not self.selected_date:
            messagebox.showinfo("情報", "日付を選択してください。")
            return

        payload = {
            "action": "get_schedule",
            "date": self.selected_date.isoformat(),
        }
        write_request(payload)
        self.result.delete("1.0", tk.END)
        self.result.insert(
            tk.END, "リクエストを送信しました。バックエンドの応答を待機します…\n"
        )

        # 応答があれば表示（任意・存在すれば）
        resp = try_read_response()
        if (
            resp
            and resp.get("action") == "get_schedule_result"
            and resp.get("date") == self.selected_date.isoformat()
        ):
            items = resp.get("schedules", [])
            if not items:
                self.result.insert(tk.END, "この日の予定はありません。\n")
            else:
                for i, sc in enumerate(items, 1):
                    line = (
                        f"[{i}] モード:{sc.get('mode','-')} "
                        f"{sc.get('name','')} {sc.get('start_date','')} {sc.get('start_time','')} -> "
                        f"{sc.get('end_date','')} {sc.get('end_time','')}\n"
                    )
                    self.result.insert(tk.END, line)
        else:
            self.result.insert(tk.END, "（response.json が存在しないか、対象外です）\n")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Freedom - カレンダー")
    root.geometry("700x650")
    CalendarWindow(root)
    root.mainloop()

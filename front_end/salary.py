import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from datetime import datetime, timedelta

# 共通のリクエスト送信モジュールをインポート
from . import request_handler

# ユーティリティのインポート
from .utils.constants import (
    DEFAULT_WAGE,
    NIGHT_RATE_MULTIPLIER,
    NIGHT_HOURS_START,
    NIGHT_HOURS_END,
    SALARY_WINDOW_WIDTH,
    SALARY_WINDOW_HEIGHT,
)


class SalaryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("給料計算")
        self.geometry(f"{SALARY_WINDOW_WIDTH}x{SALARY_WINDOW_HEIGHT}")
        self.master_root = master
        self.salaries = []  # [{'name': str, 'hours': float, 'wage': int}]
        self.fetched_schedules = []  # 取得したスケジュールを保存

        # 月選択用のフレーム
        month_frame = tk.Frame(self)
        month_frame.pack(pady=10)

        tk.Label(month_frame, text="年:").pack(side=tk.LEFT, padx=5)
        self.year_var = tk.IntVar(value=datetime.now().year)
        tk.Spinbox(
            month_frame, from_=2020, to=2030, textvariable=self.year_var, width=6
        ).pack(side=tk.LEFT)

        tk.Label(month_frame, text="月:").pack(side=tk.LEFT, padx=5)
        self.month_var = tk.IntVar(value=datetime.now().month)
        tk.Spinbox(
            month_frame, from_=1, to=12, textvariable=self.month_var, width=4
        ).pack(side=tk.LEFT)

        tk.Button(
            month_frame,
            text="シフト取得",
            command=self.fetch_mode_b_schedules,
        ).pack(side=tk.LEFT, padx=10)

        # 時給入力フレーム
        wage_frame = tk.Frame(self)
        wage_frame.pack(pady=5)

        tk.Label(wage_frame, text="通常時給:").pack(side=tk.LEFT, padx=5)
        self.wage_var = tk.IntVar(value=DEFAULT_WAGE)
        tk.Entry(wage_frame, textvariable=self.wage_var, width=10).pack(side=tk.LEFT)
        tk.Label(wage_frame, text="円").pack(side=tk.LEFT, padx=5)

        tk.Label(wage_frame, text="深夜割増率:").pack(side=tk.LEFT, padx=(20, 5))
        self.night_rate_var = tk.DoubleVar(value=NIGHT_RATE_MULTIPLIER)
        tk.Entry(wage_frame, textvariable=self.night_rate_var, width=8).pack(
            side=tk.LEFT
        )
        tk.Label(wage_frame, text="倍").pack(side=tk.LEFT, padx=5)

        tk.Button(
            wage_frame,
            text="給料計算",
            command=self.calculate_salary_from_schedules,
            bg="lightblue",
        ).pack(side=tk.LEFT, padx=10)
        """
        tk.Button(self, text="新規登録", command=self.add_salary).pack(pady=10)
        tk.Button(self, text="合計計算", command=self.calc_total).pack(pady=5)
        """
        # スクロール付きテキストウィジェット
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget = tk.Text(
            text_frame, yscrollcommand=scrollbar.set, width=80, height=20
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_widget.yview)

        self.refresh_list()

    def refresh_list(self):
        self.text_widget.delete(1.0, tk.END)
        for s in self.salaries:
            total = s["hours"] * s["wage"]
            self.text_widget.insert(
                tk.END, f"{s['name']}：{s['hours']}h × {s['wage']}円 = {total:.0f}円\n"
            )

    def calc_total(self):
        total = sum(s["hours"] * s["wage"] for s in self.salaries)
        messagebox.showinfo("合計給与", f"全員分の合計給与：{total:.0f}円")

    def fetch_mode_b_schedules(self):
        """指定した月のモードBのスケジュールを取得"""
        year = self.year_var.get()
        month = self.month_var.get()

        payload = {
            "action": "get_monthly_schedule_by_mode",
            "year": year,
            "month": month,
            "mode": "B",
        }

        request_id = request_handler.write_request(payload)
        response = request_handler.wait_for_response(
            "get_monthly_schedule_by_mode", request_id, root=self.master_root
        )

        if not response:
            messagebox.showerror("エラー", "バックエンドからの応答がありませんでした。")
            return

        if not response.get("ok"):
            error_msg = response.get("error", {}).get("message", "不明なエラー")
            messagebox.showerror("エラー", f"スケジュール取得失敗: {error_msg}")
            return

        schedules = response.get("data", {}).get("schedules", [])

        if not schedules:
            messagebox.showinfo(
                "情報", f"{year}年{month}月のモードBのスケジュールはありません。"
            )
            return

        # スケジュールを保存
        self.fetched_schedules = schedules

        messagebox.showinfo(
            "成功",
            f"{year}年{month}月のモードBのスケジュールを{len(schedules)}件取得しました。\n「給料計算」ボタンを押して計算してください。",
        )

        # 取得したスケジュールを給料計算用のリストに表示
        self.display_schedules_in_list(schedules)

    def display_schedules_in_list(self, schedules):
        """取得したスケジュールをリストボックスに表示"""
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "=== 取得したモードBのスケジュール ===\n")
        for s in schedules:
            self.text_widget.insert(
                tk.END,
                f"{s['name']}: {s['start_date']} {s['start_time']} - {s['end_date']} {s['end_time']}\n",
            )
        self.text_widget.insert(tk.END, "\n")
        self.text_widget.insert(tk.END, "=== 給料データ ===\n")
        for salary in self.salaries:
            total = salary["hours"] * salary["wage"]
            self.text_widget.insert(
                tk.END,
                f"{salary['name']}：{salary['hours']}h × {salary['wage']}円 = {total:.0f}円\n",
            )

    def calculate_working_hours(self, schedule):
        """スケジュールから勤務時間と深夜勤務時間を計算"""
        try:
            # 日時の解析
            start_datetime = datetime.strptime(
                f"{schedule['start_date']} {schedule['start_time']}", "%Y-%m-%d %H:%M"
            )
            end_datetime = datetime.strptime(
                f"{schedule['end_date']} {schedule['end_time']}", "%Y-%m-%d %H:%M"
            )

            total_hours = 0.0
            night_hours = 0.0

            current = start_datetime

            # 1分単位で処理
            while current < end_datetime:
                hour = current.hour

                # 深夜時間帯（22時～5時）の判定
                is_night = hour >= NIGHT_HOURS_START or hour < NIGHT_HOURS_END

                if is_night:
                    night_hours += 1 / 60  # 1分 = 1/60時間

                total_hours += 1 / 60
                current += timedelta(minutes=1)

            return total_hours, night_hours

        except Exception as e:
            print(f"時間計算エラー: {e}")
            return 0.0, 0.0

    def calculate_salary_from_schedules(self):
        """取得したスケジュールから給料を計算"""
        if not self.fetched_schedules:
            messagebox.showwarning(
                "警告", "先に「シフト取得」ボタンでスケジュールを取得してください。"
            )
            return

        base_wage = self.wage_var.get()
        night_rate = self.night_rate_var.get()
        night_wage = int(base_wage * night_rate)

        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "=" * 60 + "\n")
        self.text_widget.insert(
            tk.END, f"給料計算結果 ({self.year_var.get()}年{self.month_var.get()}月)\n"
        )
        self.text_widget.insert(
            tk.END,
            f"通常時給: {base_wage}円  深夜時給: {night_wage}円 (深夜割増率: {night_rate}倍)\n",
        )
        self.text_widget.insert(tk.END, "=" * 60 + "\n\n")

        total_all_hours = 0.0
        total_all_night_hours = 0.0
        total_all_salary = 0

        for schedule in self.fetched_schedules:
            total_hours, night_hours = self.calculate_working_hours(schedule)
            normal_hours = total_hours - night_hours

            # 給料計算
            normal_salary = normal_hours * base_wage
            night_salary = night_hours * night_wage
            total_salary = normal_salary + night_salary

            # 累計
            total_all_hours += total_hours
            total_all_night_hours += night_hours
            total_all_salary += total_salary

            # 表示
            self.text_widget.insert(tk.END, f"【{schedule['name']}】\n")
            self.text_widget.insert(
                tk.END,
                f"  期間: {schedule['start_date']} {schedule['start_time']} - {schedule['end_date']} {schedule['end_time']}\n",
            )
            self.text_widget.insert(
                tk.END,
                f"  通常勤務: {normal_hours:.2f}h × {base_wage}円 = {normal_salary:.0f}円\n",
            )
            self.text_widget.insert(
                tk.END,
                f"  深夜勤務: {night_hours:.2f}h × {night_wage}円 = {night_salary:.0f}円\n",
            )
            self.text_widget.insert(
                tk.END, f"  合計: {total_hours:.2f}h → {total_salary:.0f}円\n"
            )
            self.text_widget.insert(tk.END, "-" * 60 + "\n")

        # 合計表示
        self.text_widget.insert(tk.END, "\n")
        self.text_widget.insert(tk.END, "=" * 60 + "\n")
        self.text_widget.insert(tk.END, "【月間合計】\n")
        self.text_widget.insert(tk.END, f"  総勤務時間: {total_all_hours:.2f}h\n")
        self.text_widget.insert(
            tk.END, f"  深夜勤務時間: {total_all_night_hours:.2f}h\n"
        )
        self.text_widget.insert(
            tk.END, f"  通常勤務時間: {total_all_hours - total_all_night_hours:.2f}h\n"
        )
        self.text_widget.insert(tk.END, f"  総給料: {total_all_salary:.0f}円\n")
        self.text_widget.insert(tk.END, "=" * 60 + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ルートの空ウィンドウを消す（必要なら外してOK）
    SalaryWindow(root)  # これを呼ばないと画面は出ない
    root.mainloop()
    root.mainloop()

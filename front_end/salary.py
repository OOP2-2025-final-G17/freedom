import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import Tk, StringVar, IntVar
from tkinter import ttk
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class SalaryWindow(tk.Toplevel):
    def __init__(self, master: Optional[tk.Misc] = None) -> None:
        super().__init__(master)
        self.title("給料計算")
        self.geometry("400x400")
        self.salaries: List[Dict[str, float | int | str]] = (
            []
        )  # [{'name': str, 'hours': float, 'wage': int}]

        # 属性を明示的に初期化
        self.year_var: StringVar = StringVar(value=str(datetime.now().year))
        self.month_var: StringVar = StringVar(value=str(datetime.now().month))

        tk.Button(self, text="新規登録", command=self.add_salary).pack(pady=10)
        tk.Button(self, text="合計計算", command=self.calc_total).pack(pady=5)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.refresh_list()

    def add_salary(self) -> None:
        name = simpledialog.askstring(
            "氏名", "従業員名を入力してください:", parent=self
        )
        if not name:
            return

        hours_str = simpledialog.askstring(
            "労働時間", "労働時間（h）を入力してください:", parent=self
        )
        if not hours_str:
            return

        wage_str = simpledialog.askstring(
            "時給", "時給を入力してください:", parent=self
        )
        if not wage_str:
            return

        try:
            hours = float(hours_str)
            wage = int(wage_str)
        except (TypeError, ValueError):
            messagebox.showerror("入力エラー", "数値を正しく入力してください。")
            return

        self.salaries.append({"name": name, "hours": hours, "wage": wage})
        self.refresh_list()

    def refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for s in self.salaries:
            hours = float(s["hours"])
            wage = int(s["wage"])
            total = hours * wage
            self.listbox.insert(
                tk.END, f"{s['name']}：{hours}h × {wage}円 = {total:.0f}円"
            )

    def calc_total(self) -> None:
        total = sum(float(s["hours"]) * int(s["wage"]) for s in self.salaries)
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

        request_id = write_request(payload)
        response = wait_for_response(
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
                is_night = hour >= 22 or hour < 5

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
    root.withdraw()  # ルートの空ウィンドウを消す（必要なら外してOK）
    SalaryWindow(root)  # これを呼ばないと画面は出ない
    root.mainloop()

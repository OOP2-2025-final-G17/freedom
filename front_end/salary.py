import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import List, Dict, Optional


class SalaryWindow(tk.Toplevel):
    def __init__(self, master: Optional[tk.Misc] = None) -> None:
        super().__init__(master)
        self.title("給料計算")
        self.geometry("400x400")
        self.salaries: List[Dict[str, float | int | str]] = (
            []
        )  # [{'name': str, 'hours': float, 'wage': int}]

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


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ルートの空ウィンドウを消す（必要なら外してOK）
    SalaryWindow(root)  # これを呼ばないと画面は出ない
    root.mainloop()

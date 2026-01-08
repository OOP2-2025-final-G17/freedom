import tkinter as tk
from tkinter import simpledialog, messagebox

class SalaryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("給料計算")
        self.geometry("400x400")
        self.salaries = []  # [{'name': str, 'hours': float, 'wage': int}]

        tk.Button(self, text="新規登録", command=self.add_salary).pack(pady=10)
        tk.Button(self, text="合計計算", command=self.calc_total).pack(pady=5)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.refresh_list()

    def add_salary(self):
        name = simpledialog.askstring("氏名", "従業員名を入力してください:", parent=self)
        if not name:
            return
        try:
            hours = float(simpledialog.askstring("労働時間", "労働時間（h）を入力してください:", parent=self))
            wage = int(simpledialog.askstring("時給", "時給を入力してください:", parent=self))
        except (TypeError, ValueError):
            messagebox.showerror("入力エラー", "数値を正しく入力してください。")
            return
        self.salaries.append({'name': name, 'hours': hours, 'wage': wage})
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for s in self.salaries:
            total = s['hours'] * s['wage']
            self.listbox.insert(tk.END, f"{s['name']}：{s['hours']}h × {s['wage']}円 = {total:.0f}円")

    def calc_total(self):
        total = sum(s['hours'] * s['wage'] for s in self.salaries)
        messagebox.showinfo("合計給与", f"全員分の合計給与：{total:.0f}円")
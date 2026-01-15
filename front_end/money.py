import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import date


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


class MoneyWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("給料（支出）モード")
        self.geometry("480x420")

        today = date.today()
        head = ttk.Frame(self)
        head.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(head, text="集計年").pack(side=tk.LEFT)
        self.year_var = tk.IntVar(value=today.year)
        ttk.Entry(head, textvariable=self.year_var, width=6).pack(side=tk.LEFT, padx=6)

        ttk.Label(head, text="月").pack(side=tk.LEFT)
        self.month_var = tk.IntVar(value=today.month)
        ttk.Entry(head, textvariable=self.month_var, width=4).pack(side=tk.LEFT, padx=6)

        ttk.Button(head, text="計算リクエスト送信", command=self.request_calc).pack(
            side=tk.RIGHT
        )

        self.output = tk.Text(self, height=12)
        self.output.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        hint = (
            "モードB(バイト)のシフトから労働時間×時給を算出する想定。\n"
            "バックエンドが response.json に結果を書き出した場合は『最新の結果を表示』で読込できます。"
        )
        ttk.Label(self, text=hint, foreground="#555").pack(fill=tk.X, padx=10)

        ttk.Button(self, text="最新の結果を表示", command=self.try_show_result).pack(
            pady=6
        )

    def request_calc(self) -> None:
        y, m = self.year_var.get(), self.month_var.get()
        if not (1 <= m <= 12):
            messagebox.showwarning("入力エラー", "月は1-12で入力してください。")
            return
        payload = {
            "action": "calc_wage",
            "year": y,
            "month": m,
        }
        write_request(payload)
        self.output.delete("1.0", tk.END)
        self.output.insert(
            tk.END, "計算リクエストを送信しました。バックエンドの結果を待機します…\n"
        )

    def try_show_result(self) -> None:
        resp = try_read_response()
        if not resp or resp.get("action") != "calc_wage_result":
            messagebox.showinfo("情報", "response.json の結果が見つかりません。")
            return
        total_hours = resp.get("total_hours")
        total_wage = resp.get("total_wage")
        detail = resp.get("detail", [])

        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, f"総労働時間: {total_hours} 時間\n")
        self.output.insert(tk.END, f"推定給料: {total_wage} 円\n\n")
        for row in detail:
            self.output.insert(
                tk.END,
                f"{row.get('date','')}: {row.get('hours','?')}時間 × 時給{row.get('wage','?')}円 = {row.get('amount','?')}円\n",
            )


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    MoneyWindow(root)
    root.mainloop()

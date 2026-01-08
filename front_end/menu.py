import tkinter as tk
from tkinter import ttk


class MainMenu:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Freedom フロントエンド")
        self.root.geometry("360x240")

        title = ttk.Label(self.root, text="メニュー", font=("Helvetica", 16, "bold"))
        title.pack(pady=12)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=6, fill=tk.X, padx=20)

        self.btn_calendar = ttk.Button(
            btn_frame, text="カレンダー", command=self.open_calendar
        )
        self.btn_calendar.pack(fill=tk.X, pady=4)

        self.btn_change = ttk.Button(
            btn_frame, text="予定の追加/変更", command=self.open_change
        )
        self.btn_change.pack(fill=tk.X, pady=4)

        self.btn_money = ttk.Button(
            btn_frame, text="給料（支出）モード", command=self.open_money
        )
        self.btn_money.pack(fill=tk.X, pady=4)

        self.status_var = tk.StringVar(value="準備完了。操作を選んでください。")
        status = ttk.Label(self.root, textvariable=self.status_var, foreground="#555")
        status.pack(side=tk.BOTTOM, anchor=tk.W, padx=8, pady=6)

    def open_calendar(self) -> None:
        try:
            from .calender import CalendarWindow
        except Exception:
            # 相対importが失敗する場合に備えて直接import
            from calender import CalendarWindow  # type: ignore

        CalendarWindow(self.root)
        self.status_var.set("カレンダーを開きました。")

    def open_change(self) -> None:
        try:
            from .change import ChangeWindow
        except Exception:
            from change import ChangeWindow  # type: ignore

        ChangeWindow(self.root)
        self.status_var.set("予定の追加/変更を開きました。")

    def open_money(self) -> None:
        try:
            from .money import MoneyWindow
        except Exception:
            from money import MoneyWindow  # type: ignore

        MoneyWindow(self.root)
        self.status_var.set("給料（支出）モードを開きました。")


def main() -> None:
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk


class MainMenu(tk.Frame):
    def __init__(self, parent: tk.Misc, calendar_widget=None) -> None:
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        self.calendar_widget = calendar_widget  # カレンダーウィジェットへの参照を保持

        title = ttk.Label(self, text="メニュー", font=("Helvetica", 16, "bold"))
        title.pack(pady=12)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6, fill=tk.X, padx=20)

        self.btn_change = ttk.Button(
            btn_frame, text="予定の追加/変更", command=self.open_change
        )
        self.btn_change.pack(fill=tk.X, pady=4)

        self.btn_salary = ttk.Button(
            btn_frame, text="給料計算", command=self.open_salary
        )
        self.btn_salary.pack(fill=tk.X, pady=4)

        self.btn_export = ttk.Button(
            btn_frame, text="データエクスポート", command=self.export_data
        )
        self.btn_export.pack(fill=tk.X, pady=4)

        self.btn_import = ttk.Button(
            btn_frame, text="データインポート", command=self.import_data
        )
        self.btn_import.pack(fill=tk.X, pady=4)

        self.status_var = tk.StringVar(value="準備完了。操作を選んでください。")
        status = ttk.Label(self, textvariable=self.status_var, foreground="#555")
        status.pack(side=tk.BOTTOM, anchor=tk.W, padx=8, pady=6)

    def open_change(self) -> None:
        try:
            from .change import ChangeWindow
        except Exception:
            from change import ChangeWindow  # type: ignore

        ChangeWindow(self.winfo_toplevel())
        self.status_var.set("予定の追加/変更を開きました。")

    def open_salary(self):
        try:
            from .salary import SalaryWindow
        except Exception:
            from salary import SalaryWindow  # type: ignore

        SalaryWindow(self.winfo_toplevel())
        self.status_var.set("給料計算を開きました。")

    def export_data(self) -> None:
        """カレンダーウィンドウのエクスポート機能を呼び出す"""
        if self.calendar_widget:
            self.calendar_widget.export_data()
            self.status_var.set("データエクスポートを実行しました。")
        else:
            self.status_var.set("カレンダーが設定されていません。")

    def import_data(self) -> None:
        """カレンダーウィンドウのインポート機能を呼び出す"""
        if self.calendar_widget:
            self.calendar_widget.import_data()
            self.status_var.set("データインポートを実行しました。")
        else:
            self.status_var.set("カレンダーが設定されていません。")


def main() -> None:
    root = tk.Tk()
    MainMenu(root)
    root.mainloop()


if __name__ == "__main__":
    main()

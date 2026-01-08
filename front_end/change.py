import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date


def _request_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "json", "request.json")


def write_request(payload: dict) -> None:
    path = _request_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


class ChangeWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("予定の追加/変更")
        self.geometry("500x520")

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Mode
        mode_frame = ttk.LabelFrame(container, text="モード")
        mode_frame.pack(fill=tk.X, pady=6)
        self.mode_var = tk.StringVar(value="A")
        ttk.Radiobutton(
            mode_frame, text="学校(A)", value="A", variable=self.mode_var
        ).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(
            mode_frame, text="バイト(B)", value="B", variable=self.mode_var
        ).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(
            mode_frame, text="その他(NULL)", value="NULL", variable=self.mode_var
        ).pack(side=tk.LEFT, padx=6)

        # Name
        name_frame = ttk.Frame(container)
        name_frame.pack(fill=tk.X, pady=4)
        ttk.Label(name_frame, text="タイトル", width=20).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Start date/time
        sd_frame = ttk.Frame(container)
        sd_frame.pack(fill=tk.X, pady=4)
        ttk.Label(sd_frame, text="開始日(YYYY-MM-DD)", width=20).pack(side=tk.LEFT)
        self.start_date = ttk.Entry(sd_frame)
        self.start_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.start_date.insert(0, date.today().isoformat())

        st_frame = ttk.Frame(container)
        st_frame.pack(fill=tk.X, pady=4)
        ttk.Label(st_frame, text="開始時刻(HH:MM)", width=20).pack(side=tk.LEFT)
        self.start_time = ttk.Entry(st_frame)
        self.start_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.start_time.insert(0, "09:00")

        # End date/time
        ed_frame = ttk.Frame(container)
        ed_frame.pack(fill=tk.X, pady=4)
        ttk.Label(ed_frame, text="終了日(YYYY-MM-DD)", width=20).pack(side=tk.LEFT)
        self.end_date = ttk.Entry(ed_frame)
        self.end_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.end_date.insert(0, date.today().isoformat())

        et_frame = ttk.Frame(container)
        et_frame.pack(fill=tk.X, pady=4)
        ttk.Label(et_frame, text="終了時刻(HH:MM)", width=20).pack(side=tk.LEFT)
        self.end_time = ttk.Entry(et_frame)
        self.end_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.end_time.insert(0, "18:00")

        # Action buttons
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="登録/更新", command=self.submit).pack(side=tk.RIGHT)

        self.status_var = tk.StringVar(value="入力して『登録/更新』を押してください。")
        ttk.Label(self, textvariable=self.status_var, foreground="#555").pack(
            side=tk.BOTTOM, anchor=tk.W, padx=10, pady=8
        )

    def submit(self) -> None:
        mode = self.mode_var.get()
        payload = {
            "action": "save_schedule",
            "mode": mode,
            "name": self.name_entry.get().strip(),
            "start_date": self.start_date.get().strip(),
            "start_time": self.start_time.get().strip(),
            "end_date": self.end_date.get().strip(),
            "end_time": self.end_time.get().strip(),
        }

        if not payload["name"]:
            messagebox.showwarning("入力不足", "タイトルを入力してください。")
            return

        write_request(payload)
        self.status_var.set(
            "リクエストを送信しました。バックエンドで処理してください。"
        )
        messagebox.showinfo("送信", "request.json に書き込みました。")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ChangeWindow(root)
    root.mainloop()

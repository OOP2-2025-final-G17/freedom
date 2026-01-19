import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

# 共通のリクエスト送信モジュールをインポート
from .request_handler import write_request

# ユーティリティのインポート
from .utils.constants import (
    DEFAULT_START_TIME,
    DEFAULT_END_TIME,
    CHANGE_WINDOW_WIDTH,
    CHANGE_WINDOW_HEIGHT,
    TASK_ID_FILE,
)
from .utils.validators import validate_schedule_format


def _id_path() -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, TASK_ID_FILE)


def get_next_task_id() -> int:
    """タスク用の自動採番IDを返す。json/task_id.json に保存。"""
    path = _id_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    last = 0
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                last = int(data.get("last_id", 0))
        except Exception:
            last = 0
    next_id = last + 1
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"last_id": next_id}, f, ensure_ascii=False, indent=2)
    except Exception:
        # 書き込み失敗でもIDは返す
        pass
    return next_id


class ChangeWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc | None = None,
        *,
        existing_schedule: dict | None = None,
        on_success=None,
    ) -> None:
        super().__init__(master)
        self.title("予定の追加/変更")
        self.geometry(f"{CHANGE_WINDOW_WIDTH}x{CHANGE_WINDOW_HEIGHT}")
        self._existing = existing_schedule
        self._on_success = on_success

        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Mode
        mode_frame = ttk.LabelFrame(container, text="モード")
        mode_frame.pack(fill=tk.X, pady=6)
        default_mode = "A"
        if self._existing is not None:
            default_mode = str(self._existing.get("mode", default_mode))
        self.mode_var = tk.StringVar(value=default_mode)
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
        if self._existing is not None:
            self.name_entry.insert(0, str(self._existing.get("name", "")))

        # Start date/time
        sd_frame = ttk.Frame(container)
        sd_frame.pack(fill=tk.X, pady=4)
        ttk.Label(sd_frame, text="開始日(YYYY-MM-DD)", width=20).pack(side=tk.LEFT)
        self.start_date = ttk.Entry(sd_frame)
        self.start_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.start_date.insert(
            0,
            str(
                (
                    self._existing.get("start_date")
                    if self._existing
                    else date.today().isoformat()
                )
            ),
        )

        st_frame = ttk.Frame(container)
        st_frame.pack(fill=tk.X, pady=4)
        ttk.Label(st_frame, text="開始時刻(HH:MM)", width=20).pack(side=tk.LEFT)
        self.start_time = ttk.Entry(st_frame)
        self.start_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.start_time.insert(
            0,
            str(
                self._existing.get("start_time", DEFAULT_START_TIME)
                if self._existing
                else DEFAULT_START_TIME
            ),
        )

        # End date/time
        ed_frame = ttk.Frame(container)
        ed_frame.pack(fill=tk.X, pady=4)
        ttk.Label(ed_frame, text="終了日(YYYY-MM-DD)", width=20).pack(side=tk.LEFT)
        self.end_date = ttk.Entry(ed_frame)
        self.end_date.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.end_date.insert(
            0,
            str(
                (
                    self._existing.get("end_date")
                    if self._existing
                    else date.today().isoformat()
                )
            ),
        )

        et_frame = ttk.Frame(container)
        et_frame.pack(fill=tk.X, pady=4)
        ttk.Label(et_frame, text="終了時刻(HH:MM)", width=20).pack(side=tk.LEFT)
        self.end_time = ttk.Entry(et_frame)
        self.end_time.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.end_time.insert(
            0,
            str(
                self._existing.get("end_time", DEFAULT_END_TIME)
                if self._existing
                else DEFAULT_END_TIME
            ),
        )

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
        name = self.name_entry.get().strip()
        start_date_str = self.start_date.get().strip()
        start_time_str = self.start_time.get().strip()
        end_date_str = self.end_date.get().strip()
        end_time_str = self.end_time.get().strip()

        # バリデーション実行
        is_valid, error_msg = validate_schedule_format(
            name, mode, start_date_str, start_time_str, end_date_str, end_time_str
        )

        if not is_valid:
            messagebox.showwarning("入力エラー", error_msg)
            return

        # 追加/更新のアクション切替
        if self._existing is not None:
            payload = {
                "action": "update_schedule",
                # 既存IDがあれば引き継ぐ
                "id": self._existing.get("id"),
                "mode": mode,
                "name": name,
                "start_date": start_date_str,
                "start_time": start_time_str,
                "end_date": end_date_str,
                "end_time": end_time_str,
            }
        else:
            payload = {
                "action": "add_schedule",
                "mode": mode,
                "name": name,
                "start_date": start_date_str,
                "start_time": start_time_str,
                "end_date": end_date_str,
                "end_time": end_time_str,
            }

        request_id = write_request(payload)
        if self._existing is not None:
            self.status_var.set(
                "更新リクエストを送信しました。バックエンドで処理してください。"
            )
            messagebox.showinfo(
                "送信", "更新リクエストを request.json に書き込みました。"
            )
        else:
            self.status_var.set(
                "リクエストを送信しました。バックエンドで処理してください。"
            )
            messagebox.showinfo("送信", "request.json に書き込みました。")

        # コールバックを実行して親画面を更新（request_idを渡す）
        if self._on_success:
            self._on_success(request_id)

        # ダイアログを閉じる
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    ChangeWindow(root)
    root.mainloop()

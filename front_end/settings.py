"""
ユーザー設定ウィンドウ
通勤・通学時間、時給などの設定を編集します
"""

import tkinter as tk
from tkinter import ttk, messagebox

from .utils.settings_manager import get_settings_manager


class SettingsWindow(tk.Toplevel):
    """設定ウィンドウ"""

    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.title("ユーザー設定")
        self.geometry("500x450")

        # 設定マネージャーを取得
        self.settings_mgr = get_settings_manager()
        self.current_settings = self.settings_mgr.get_all_settings()

        # メインフレーム
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # タイトル
        title = ttk.Label(
            main_frame, text="ユーザー設定", font=("Helvetica", 14, "bold")
        )
        title.pack(pady=10)

        # 設定フレーム
        settings_frame = ttk.LabelFrame(main_frame, text="設定項目", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 通勤時間
        self._add_setting_row(
            settings_frame,
            "通勤時間（分）:",
            "commute_time",
            0,
            1440,
        )

        # 通学時間
        self._add_setting_row(
            settings_frame,
            "通学時間（分）:",
            "school_time",
            0,
            1440,
        )

        # 時給
        self._add_setting_row(
            settings_frame,
            "時給（円）:",
            "hourly_wage",
            0,
            100000,
        )

        # 深夜割増率
        self._add_setting_row(
            settings_frame,
            "深夜割増率（倍）:",
            "night_rate",
            1.0,
            3.0,
            is_float=True,
        )

        # 深夜開始時刻
        self._add_setting_row(
            settings_frame,
            "深夜開始時刻（時）:",
            "night_start",
            0,
            23,
        )

        # 深夜終了時刻
        self._add_setting_row(
            settings_frame,
            "深夜終了時刻（時）:",
            "night_end",
            0,
            23,
        )

        # ボタンフレーム
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=15)

        ttk.Button(btn_frame, text="保存", command=self.save_settings).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="デフォルト", command=self.reset_to_default).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(btn_frame, text="キャンセル", command=self.destroy).pack(
            side=tk.RIGHT, padx=5
        )

        # ステータスラベル
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self, textvariable=self.status_var, foreground="#555")
        status.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=8)

    def _add_setting_row(
        self,
        parent,
        label_text: str,
        key: str,
        min_val: int | float,
        max_val: int | float,
        is_float: bool = False,
    ) -> None:
        """設定行を追加"""
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=8)

        ttk.Label(row, text=label_text, width=20).pack(side=tk.LEFT)

        entry = ttk.Entry(row, width=15)
        entry.pack(side=tk.LEFT, padx=10)

        # 現在の値を表示
        current_value = self.current_settings.get(key)
        if is_float:
            entry.insert(0, f"{float(current_value):.2f}")
        else:
            entry.insert(0, str(int(current_value)))

        # 検証用のスピンボックスの代わりにEntry を使用
        # 値の範囲表示
        ttk.Label(row, text=f"({min_val}-{max_val})", foreground="#999").pack(
            side=tk.LEFT
        )

        # キーを属性として保存（後で参照するため）
        if not hasattr(self, "_entries"):
            self._entries = {}
        self._entries[key] = (entry, is_float, min_val, max_val)

    def save_settings(self) -> None:
        """設定を保存"""
        new_settings = self.current_settings.copy()

        # 各エントリーから値を取得
        for key, (entry, is_float, min_val, max_val) in self._entries.items():
            try:
                value_str = entry.get().strip()
                if is_float:
                    value = float(value_str)
                else:
                    value = int(value_str)

                new_settings[key] = value
            except ValueError:
                messagebox.showwarning(
                    "入力エラー",
                    f"{key} の値が不正です。数値を入力してください。",
                )
                return

        # バリデーション
        is_valid, error_msg = self.settings_mgr.validate_settings(new_settings)
        if not is_valid:
            messagebox.showwarning("バリデーションエラー", error_msg)
            return

        # 保存
        if self.settings_mgr.save_settings(new_settings):
            self.status_var.set("設定を保存しました。")
            messagebox.showinfo("成功", "設定を保存しました。")
            self.current_settings = new_settings
        else:
            messagebox.showerror("エラー", "設定の保存に失敗しました。")

    def reset_to_default(self) -> None:
        """デフォルト設定にリセット"""
        if messagebox.askyesno(
            "確認", "設定をデフォルト値にリセットしてもよろしいですか？"
        ):
            if self.settings_mgr.reset_to_default():
                self.current_settings = self.settings_mgr.get_all_settings()
                self._refresh_display()
                self.status_var.set("デフォルト設定に戻しました。")
                messagebox.showinfo("成功", "設定をリセットしました。")
            else:
                messagebox.showerror("エラー", "設定のリセットに失敗しました。")

    def _refresh_display(self) -> None:
        """画面を更新"""
        for key, (entry, is_float, _, _) in self._entries.items():
            entry.delete(0, tk.END)
            value = self.current_settings.get(key)
            if is_float:
                entry.insert(0, f"{float(value):.2f}")
            else:
                entry.insert(0, str(int(value)))


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    SettingsWindow(root)
    root.mainloop()

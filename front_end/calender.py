import datetime as dt
import calendar as pycal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import json

# 共通のリクエスト送信モジュールをインポート
from .request_handler import write_request, wait_for_response, try_read_response

# デバッグモード（False にするとログが出ない）
DEBUG = False


class CalendarWindow(tk.Frame):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)

        today = dt.date.today()
        self.year = tk.IntVar(value=today.year)
        self.month = tk.IntVar(value=today.month)
        self.selected_date: dt.date | None = None
        self.selected_button: tk.Widget | None = None  # 追加：選択中のボタンを追跡

        # カスタムスタイルの設定（修正）
        style = ttk.Style()
        style.configure(
            "Today.TButton", background="#ffffcc"
        )  # 今日の日付用（薄い黄色）
        style.configure(
            "Selected.TButton", background="#ccccff"
        )  # 選択日付用（薄い青色）
        # 追加：土曜日・日曜日用のスタイル
        style.configure("Saturday.TButton", foreground="blue")
        style.configure("Sunday.TButton", foreground="red")
        style.configure("Saturday.TLabel", foreground="blue")
        style.configure("Sunday.TLabel", foreground="red")
        self.current_items: list[dict] = []

        control = ttk.Frame(self)
        control.pack(fill=tk.X, padx=10, pady=8)

        prev_btn = ttk.Button(control, text="<", width=3, command=self.prev_month)
        prev_btn.pack(side=tk.LEFT)

        # 追加：「今日」ボタン
        today_btn = ttk.Button(control, text="今日", width=4, command=self.go_to_today)
        today_btn.pack(side=tk.LEFT, padx=5)

        self.title_var = tk.StringVar()
        title_lbl = ttk.Label(
            control, textvariable=self.title_var, font=("Helvetica", 14, "bold")
        )
        title_lbl.pack(side=tk.LEFT, expand=True)

        next_btn = ttk.Button(control, text=">", width=3, command=self.next_month)
        next_btn.pack(side=tk.RIGHT)

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=6)

        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=6)

        self.sel_var = tk.StringVar(value="日付未選択")
        ttk.Label(action_frame, textvariable=self.sel_var).pack(side=tk.LEFT)

        ttk.Button(
            action_frame, text="この日の予定を取得", command=self.request_day
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            action_frame, text="月全体の予定を取得", command=self.request_month
        ).pack(side=tk.RIGHT, padx=5)

        # データエクスポート/インポートボタン
        ttk.Button(action_frame, text="エクスポート", command=self.export_data).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(action_frame, text="インポート", command=self.import_data).pack(
            side=tk.LEFT, padx=5
        )

        # self.result = tk.Text(self, height=10)
        # 予定リストと操作ボタン
        list_frame = ttk.LabelFrame(self, text="予定一覧（選択して操作）")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

        self.tree = ttk.Treeview(
            list_frame,
            columns=("mode", "name", "start", "end"),
            show="headings",
            height=8,
        )
        self.tree.heading("mode", text="モード")
        self.tree.heading("name", text="タイトル")
        self.tree.heading("start", text="開始")
        self.tree.heading("end", text="終了")
        self.tree.column("mode", width=60, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("start", width=140, anchor="center")
        self.tree.column("end", width=140, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 6))

        op_frame = ttk.Frame(list_frame)
        op_frame.pack(fill=tk.X)
        ttk.Button(op_frame, text="選択を削除", command=self.delete_selected).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(op_frame, text="選択を更新", command=self.update_selected).pack(
            side=tk.LEFT, padx=4
        )

        # 取得結果のメッセージ表示
        self.result = tk.Text(self, height=6)
        self.result.pack(fill=tk.BOTH, expand=False, padx=10, pady=6)

        self.draw_calendar()

    def draw_calendar(self) -> None:
        # 既存ウィジェット削除
        for w in self.grid_frame.winfo_children():
            w.destroy()

        y, m = self.year.get(), self.month.get()
        self.title_var.set(f"{y}年 {m}月")

        # 曜日ヘッダ
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        for i, wd in enumerate(weekdays):
            # 土曜日と日曜日の色分け（修正）
            if i == 5:  # 土曜日
                label = ttk.Label(
                    self.grid_frame, text=wd, anchor="center", style="Saturday.TLabel"
                )
            elif i == 6:  # 日曜日
                label = ttk.Label(
                    self.grid_frame, text=wd, anchor="center", style="Sunday.TLabel"
                )
            else:
                label = ttk.Label(self.grid_frame, text=wd, anchor="center")
            label.grid(row=0, column=i, sticky="nsew")

        cal = pycal.Calendar(firstweekday=0)  # 0: Monday
        row = 1
        today = dt.date.today()  # 追加：今日の日付を取得

        for week in cal.monthdatescalendar(y, m):
            for col, day in enumerate(week):
                is_current_month = day.month == m
                is_today = day == today  # 追加：今日かどうか
                is_selected = self.selected_date == day  # 追加：選択中かどうか

                # スタイル名を決定（修正）
                style_name = ""
                weekday = day.weekday()  # 0=月曜, 6=日曜

                if is_current_month:
                    if weekday == 6:  # 日曜日
                        style_name = "Sunday.TButton"
                    elif weekday == 5:  # 土曜日
                        style_name = "Saturday.TButton"

                # 今日の日付または選択中の日付の場合は優先
                if is_today and is_current_month:
                    style_name = "Today.TButton"
                if is_selected and is_current_month:
                    style_name = "Selected.TButton"

                # ボタンを作成
                if style_name:
                    btn = ttk.Button(
                        self.grid_frame,
                        text=str(day.day),
                        width=4,
                        command=lambda d=day: self.select_date(d),
                        style=style_name,
                    )
                else:
                    btn = ttk.Button(
                        self.grid_frame,
                        text=str(day.day),
                        width=4,
                        command=lambda d=day: self.select_date(d),
                    )

                if is_selected and is_current_month:
                    self.selected_button = btn

                if not is_current_month:
                    btn.state(["disabled"])  # 当月以外は無効

                btn.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
            row += 1

        # 均等拡張
        for r in range(row + 1):
            self.grid_frame.rowconfigure(r, weight=1)
        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)

    def select_date(self, day: dt.date) -> None:
        self.selected_date = day
        self.sel_var.set(f"選択: {day.isoformat()}")
        self.draw_calendar()  # 変更：再描画して選択状態を反映

    def prev_month(self) -> None:
        y, m = self.year.get(), self.month.get()
        if m == 1:
            self.year.set(y - 1)
            self.month.set(12)
        else:
            self.month.set(m - 1)
        self.draw_calendar()

    def next_month(self) -> None:
        y, m = self.year.get(), self.month.get()
        if m == 12:
            self.year.set(y + 1)
            self.month.set(1)
        else:
            self.month.set(m + 1)
        self.draw_calendar()

    # 追加：「今日に戻る」メソッド
    def go_to_today(self) -> None:
        today = dt.date.today()
        self.year.set(today.year)
        self.month.set(today.month)
        self.selected_date = today
        self.draw_calendar()

    def request_day(self) -> None:
        if not self.selected_date:
            messagebox.showinfo("情報", "日付を選択してください。")
            return

        payload = {
            "action": "get_schedule",
            "date": self.selected_date.isoformat(),
        }
        request_id = write_request(payload)
        self.result.delete("1.0", tk.END)
        self.result.insert(
            tk.END, "リクエストを送信しました。バックエンドの応答を待機します…\n"
        )

        # 更新を強制的に画面に反映
        self.update_idletasks()

        # レスポンスが返ってくるまで待機（期待するリクエストIDと日付のレスポンスを待つ）
        expected_date = self.selected_date.isoformat()
        resp = wait_for_response(
            "get_schedule",
            request_id,
            expected_data_validator=lambda r: r.get("data", {}).get("date")
            == expected_date,
            timeout=10.0,
            root=self.master,
            debug=True,
        )

        # ツリー更新
        self.tree.delete(*self.tree.get_children())
        self.current_items = []

        if resp and resp.get("ok") is True:
            data = resp.get("data", {})
            if data.get("date") == self.selected_date.isoformat():
                items = data.get("schedules", [])
                if not items:
                    self.result.insert(tk.END, "この日の予定はありません。\n")
                else:
                    for sc in items:
                        mode = sc.get("mode", "-")
                        name = sc.get("name", "")
                        start = f"{sc.get('start_date','')} {sc.get('start_time','')}"
                        end = f"{sc.get('end_date','')} {sc.get('end_time','')}"
                        self.tree.insert("", tk.END, values=(mode, name, start, end))
                        self.current_items.append(sc)
                    self.result.insert(
                        tk.END, f"{len(items)}件の予定を取得しました。\n"
                    )
            else:
                self.result.insert(tk.END, "日付が一致しません。\n")
        elif resp and resp.get("ok") is False:
            error = resp.get("error", {})
            self.result.insert(
                tk.END, f"エラー: {error.get('message', '不明なエラー')}\n"
            )
        else:
            self.result.insert(
                tk.END, "タイムアウト: バックエンドからの応答がありませんでした。\n"
            )

    def _get_selection_index(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("情報", "予定を1件選択してください。")
            return None
        item_id = sel[0]
        # 表示順 == current_items の順
        index = self.tree.index(item_id)
        if index is None or index < 0 or index >= len(self.current_items):
            messagebox.showwarning("エラー", "選択中のアイテムを特定できません。")
            return None
        return index

    def delete_selected(self) -> None:
        if not self.selected_date:
            messagebox.showinfo("情報", "日付を選択してください。")
            return
        idx = self._get_selection_index()
        if idx is None:
            return
        target = self.current_items[idx]
        sid = target.get("id")
        if sid is None:
            messagebox.showwarning(
                "エラー", "この予定にはIDがありません。削除にはIDが必要です。"
            )
            return

        # DBが付与した一意IDを使って削除
        payload = {
            "action": "delete_schedule",
            "id": sid,
        }
        request_id = write_request(payload)
        self.result.delete("1.0", tk.END)
        self.result.insert(
            tk.END, "削除リクエストを送信しました。バックエンドの応答を待機します…\n"
        )

        # 更新を強制的に画面に反映
        self.update_idletasks()

        # レスポンスが返ってくるまで待機
        resp = wait_for_response(
            "delete_schedule", request_id, timeout=10.0, root=self.master, debug=True
        )

        if resp and resp.get("ok") is True:
            self.result.insert(tk.END, "削除しました。予定を再取得しています...\n")
            self.update_idletasks()
            # 削除成功後、予定を再取得
            self.request_day()
        elif resp and resp.get("ok") is False:
            error = resp.get("error", {})
            self.result.insert(
                tk.END, f"削除エラー: {error.get('message', '不明なエラー')}\n"
            )
        else:
            self.result.insert(
                tk.END, "タイムアウト: バックエンドからの応答がありませんでした。\n"
            )

    def update_selected(self) -> None:
        if not self.selected_date:
            messagebox.showinfo("情報", "日付を選択してください。")
            return
        idx = self._get_selection_index()
        if idx is None:
            return
        target = self.current_items[idx]
        # 変更ウィンドウを既存値で開く
        try:
            from .change import ChangeWindow
        except Exception:
            from change import ChangeWindow  # type: ignore

        # 更新完了時のコールバック
        def on_update_success():
            self.result.delete("1.0", tk.END)
            self.result.insert(tk.END, "更新しました。予定を再取得しています...\n")
            self.update_idletasks()
            # 更新成功後、予定を再取得
            self.request_day()

        ChangeWindow(
            self.winfo_toplevel(),
            existing_schedule=target,
            on_success=on_update_success,
        )
        self.result.delete("1.0", tk.END)
        self.result.insert(tk.END, "更新ダイアログを開きました。\n")

    def request_month(self) -> None:
        """月全体の予定を取得する"""
        y, m = self.year.get(), self.month.get()

        payload = {
            "action": "get_monthly_schedule",
            "year": y,
            "month": m,
        }
        request_id = write_request(payload)
        self.result.delete("1.0", tk.END)
        self.result.insert(tk.END, f"{y}年{m}月の予定を取得中...\n")

        # 更新を強制的に画面に反映
        self.update_idletasks()

        # レスポンスが返ってくるまで待機
        resp = wait_for_response(
            "get_monthly_schedule",
            request_id,
            timeout=10.0,
            root=self.master,
        )

        # ツリー更新
        self.tree.delete(*self.tree.get_children())
        self.current_items = []

        if resp and resp.get("ok") is True:
            data = resp.get("data", {})
            items = data.get("schedules", [])
            if not items:
                self.result.insert(tk.END, f"{y}年{m}月の予定はありません。\n")
            else:
                for sc in items:
                    mode = sc.get("mode", "-")
                    name = sc.get("name", "")
                    start = f"{sc.get('start_date','')} {sc.get('start_time','')}"
                    end = f"{sc.get('end_date','')} {sc.get('end_time','')}"
                    self.tree.insert("", tk.END, values=(mode, name, start, end))
                    self.current_items.append(sc)
                self.result.insert(
                    tk.END, f"{y}年{m}月の予定を{len(items)}件取得しました。\n"
                )
        elif resp and resp.get("ok") is False:
            error = resp.get("error", {})
            self.result.insert(
                tk.END, f"エラー: {error.get('message', '不明なエラー')}\n"
            )
        else:
            self.result.insert(
                tk.END, "タイムアウト: バックエンドからの応答がありませんでした。\n"
            )

    def export_data(self) -> None:
        """全ての予定をJSONファイルにエクスポート"""
        payload = {
            "action": "get_all_schedules",
        }
        request_id = write_request(payload)
        self.result.delete("1.0", tk.END)
        self.result.insert(tk.END, "データをエクスポート中...\n")
        self.update_idletasks()

        resp = wait_for_response(
            "get_all_schedules",
            request_id,
            timeout=10.0,
            root=self.master,
        )

        if resp and resp.get("ok") is True:
            data = resp.get("data", {})
            schedules = data.get("schedules", [])

            # ファイル保存ダイアログ
            file_path = filedialog.asksaveasfilename(
                title="エクスポート先を選択",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"schedules_export_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )

            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(schedules, f, ensure_ascii=False, indent=2)
                    self.result.insert(
                        tk.END, f"{len(schedules)}件の予定をエクスポートしました。\n"
                    )
                    self.result.insert(tk.END, f"保存先: {file_path}\n")
                    messagebox.showinfo(
                        "成功", f"{len(schedules)}件の予定をエクスポートしました。"
                    )
                except Exception as e:
                    self.result.insert(tk.END, f"ファイル保存エラー: {e}\n")
                    messagebox.showerror("エラー", f"ファイル保存に失敗しました: {e}")
            else:
                self.result.insert(tk.END, "エクスポートがキャンセルされました。\n")
        elif resp and resp.get("ok") is False:
            error = resp.get("error", {})
            self.result.insert(
                tk.END, f"エラー: {error.get('message', '不明なエラー')}\n"
            )
            messagebox.showerror("エラー", error.get("message", "不明なエラー"))
        else:
            self.result.insert(
                tk.END, "タイムアウト: バックエンドからの応答がありませんでした。\n"
            )
            messagebox.showerror("エラー", "バックエンドからの応答がありませんでした。")

    def import_data(self) -> None:
        """JSONファイルから予定をインポート"""
        file_path = filedialog.askopenfilename(
            title="インポートするファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                schedules = json.load(f)

            if not isinstance(schedules, list):
                messagebox.showerror(
                    "エラー", "無効なファイル形式です。スケジュールのリストが必要です。"
                )
                return

            # IDフィールドを削除（新規作成するため）
            for sc in schedules:
                if "id" in sc:
                    del sc["id"]

            payload = {
                "action": "import_schedules",
                "schedules": schedules,
            }
            request_id = write_request(payload)
            self.result.delete("1.0", tk.END)
            self.result.insert(tk.END, f"{len(schedules)}件の予定をインポート中...\n")
            self.update_idletasks()

            resp = wait_for_response(
                "import_schedules",
                request_id,
                timeout=30.0,
                root=self.master,
            )

            if resp and resp.get("ok") is True:
                data = resp.get("data", {})
                imported = data.get("imported", 0)
                errors = data.get("errors", [])

                self.result.insert(
                    tk.END, f"{imported}件の予定をインポートしました。\n"
                )
                if errors:
                    self.result.insert(
                        tk.END, f"{len(errors)}件のエラーがありました:\n"
                    )
                    for err in errors[:10]:  # 最初の10件のみ表示
                        self.result.insert(tk.END, f"  - {err}\n")
                    if len(errors) > 10:
                        self.result.insert(tk.END, f"  ... 他{len(errors) - 10}件\n")

                messagebox.showinfo("完了", f"{imported}件の予定をインポートしました。")

                # 現在表示中の日付/月を再取得
                if self.selected_date:
                    self.request_day()
                else:
                    self.request_month()

            elif resp and resp.get("ok") is False:
                error = resp.get("error", {})
                self.result.insert(
                    tk.END, f"エラー: {error.get('message', '不明なエラー')}\n"
                )
                messagebox.showerror("エラー", error.get("message", "不明なエラー"))
            else:
                self.result.insert(
                    tk.END, "タイムアウト: バックエンドからの応答がありませんでした。\n"
                )
                messagebox.showerror(
                    "エラー", "バックエンドからの応答がありませんでした。"
                )

        except json.JSONDecodeError as e:
            messagebox.showerror("エラー", f"JSONファイルの解析に失敗しました: {e}")
        except Exception as e:
            messagebox.showerror("エラー", f"インポート中にエラーが発生しました: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Freedom - カレンダー")
    root.geometry("700x650")
    CalendarWindow(root)
    root.mainloop()

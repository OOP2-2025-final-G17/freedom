import os
import json
import datetime as dt
import calendar as pycal
import tkinter as tk
from tkinter import ttk, messagebox
import time
import uuid

# デバッグモード（False にするとログが出ない）
DEBUG = False


def _paths():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req = os.path.join(base, "json", "request.json")
    res = os.path.join(base, "json", "response.json")
    return req, res


<<<<<<< HEAD
def write_request(payload: dict) -> str:
    """リクエストを送信し、リクエストIDを返す"""
    req, res = _paths()
    os.makedirs(os.path.dirname(req), exist_ok=True)
    
    # リクエスト送信前に古いレスポンスを削除
    try:
        if os.path.exists(res):
            os.remove(res)
        time.sleep(0.2)  # 削除完了を確実にする
    except Exception:
        pass

    # リクエストに一意のIDをつける
    request_id = str(uuid.uuid4())
    payload["_request_id"] = request_id

=======
def write_request(payload: dict) -> None:
    req, res = _paths()
    
    # response.json を初期化
    os.makedirs(os.path.dirname(res), exist_ok=True)
    with open(res, "w", encoding="utf-8") as f:
        f.write("")
    
    # request.json にペイロード書き込み
    os.makedirs(os.path.dirname(req), exist_ok=True)
>>>>>>> 049d2a18d56fff41f356fbeae46250f3f390dcce
    with open(req, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    
    return request_id


def try_read_response() -> dict | None:
    _, res = _paths()
    if not os.path.exists(res):
        return None
    try:
        with open(res, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


<<<<<<< HEAD
def wait_for_response(
    expected_action: str, expected_request_id: str, expected_data_validator=None, timeout: float = 10.0, root=None
) -> dict | None:
    """指定されたリクエストIDのレスポンスまで待機する"""
    import sys
    from datetime import datetime
    
=======
def wait_for_response(expected_action: str, timeout: float = 30.0) -> dict | None:
    """レスポンスファイルが作成されて期待するアクションが返されるまで待機する"""
>>>>>>> 049d2a18d56fff41f356fbeae46250f3f390dcce
    _, res = _paths()
    start_time = time.time()
    print(f"[{datetime.now()}] wait_for_response started: action={expected_action}, request_id={expected_request_id}", file=sys.stderr, flush=True)

    while time.time() - start_time < timeout:
        # Tkinter event loop を処理（バックエンドが実行されるようにする）
        if root:
            root.update()
        
        elapsed = time.time() - start_time
        # ファイルが存在するかチェック
        if not os.path.exists(res):
            print(f"[{datetime.now()}] [{elapsed:.2f}s] Response file not found", file=sys.stderr, flush=True)
            time.sleep(0.05)
            continue

        try:
            time.sleep(0.05)  # ファイル書き込み完了を待つ
            with open(res, "r", encoding="utf-8") as f:
                content = f.read().strip()
                print(f"[{datetime.now()}] [{elapsed:.2f}s] Response content: {content[:100]}", file=sys.stderr, flush=True)
                if not content:  # 空ファイルの場合はスキップ
                    print(f"[{datetime.now()}] [{elapsed:.2f}s] Response file is empty", file=sys.stderr, flush=True)
                    time.sleep(0.05)
                    continue

                resp = json.loads(content)
                action = resp.get("action")
                request_id = resp.get("_request_id")
                
                print(f"[{datetime.now()}] [{elapsed:.2f}s] Parsed response: action={action}, request_id={request_id}", file=sys.stderr, flush=True)

                # 期待されるアクション＆リクエストIDのレスポンスか確認
                if action == expected_action and request_id == expected_request_id:
                    print(f"[{datetime.now()}] [{elapsed:.2f}s] Matching response found!", file=sys.stderr, flush=True)
                    # 追加の検証があればチェック
                    if expected_data_validator is None or expected_data_validator(resp):
                        return resp
                    else:
                        # 検証失敗：異なるデータの場合は待機を続ける
                        print(f"[{datetime.now()}] [{elapsed:.2f}s] Validator failed", file=sys.stderr, flush=True)
                        time.sleep(0.05)
                else:
                    # 異なるリクエストIDまたはアクションの場合は無視して待機を続ける
                    print(f"[{datetime.now()}] [{elapsed:.2f}s] Not matching (expected action={expected_action}, request_id={expected_request_id})", file=sys.stderr, flush=True)
                    time.sleep(0.05)

        except (json.JSONDecodeError, IOError) as e:
            # JSONパースエラーまたはファイル読み込みエラーは無視して再試行
            print(f"[{datetime.now()}] [{elapsed:.2f}s] Error reading response: {e}", file=sys.stderr, flush=True)
            time.sleep(0.05)
            continue

    print(f"[{datetime.now()}] wait_for_response timeout!", file=sys.stderr, flush=True)
    return None


class CalendarWindow(tk.Frame):
    def __init__(self, master: tk.Misc | None = None) -> None:
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True)

        today = dt.date.today()
        self.year = tk.IntVar(value=today.year)
        self.month = tk.IntVar(value=today.month)
        self.selected_date: dt.date | None = None
        self.current_items: list[dict] = []

        control = ttk.Frame(self)
        control.pack(fill=tk.X, padx=10, pady=8)

        prev_btn = ttk.Button(control, text="<", width=3, command=self.prev_month)
        prev_btn.pack(side=tk.LEFT)

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
        ).pack(side=tk.RIGHT)

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
            ttk.Label(self.grid_frame, text=wd, anchor="center").grid(
                row=0, column=i, sticky="nsew"
            )

        cal = pycal.Calendar(firstweekday=0)  # 0: Monday
        row = 1
        for week in cal.monthdatescalendar(y, m):
            for col, day in enumerate(week):
                is_current_month = day.month == m
                btn = ttk.Button(
                    self.grid_frame,
                    text=str(day.day),
                    width=4,
                    command=lambda d=day: self.select_date(d),
                )
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
        resp = wait_for_response("delete_schedule", request_id, timeout=10.0, root=self.master)

        if resp and resp.get("ok") is True:
            self.result.insert(tk.END, "削除しました。\n")
            # ツリーから削除
            self.tree.delete(*self.tree.get_children())
            self.current_items = []
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

        ChangeWindow(self.winfo_toplevel(), existing_schedule=target)
        self.result.delete("1.0", tk.END)
        self.result.insert(tk.END, "更新ダイアログを開きました。\n")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Freedom - カレンダー")
    root.geometry("700x650")
    CalendarWindow(root)
    root.mainloop()

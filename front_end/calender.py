import datetime
import calendar
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from task_test import TaskDetailWindow, TaskManager
import json
import os


class calWidget(tk.Frame):
    def __init__(self, master=None, cnf={}, **kw):

        tk.Frame.__init__(self, master, cnf, **kw)
        self.configure(bg="#f5f5f5")

        # 現在の日付を取得
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month
        self.today = now.day

        # タスク管理の初期化
        self.task_manager = TaskManager("tasks.json")

        # メインコンテナ
        main_container = tk.Frame(self, bg="#f5f5f5")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左側パネル（月の小カレンダー）
        left_panel = tk.Frame(main_container, bg="white", relief=tk.SOLID, bd=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # 月の小カレンダーヘッダー
        mini_header = tk.Frame(left_panel, bg="#1f77d4")
        mini_header.pack(fill=tk.X)

        self.mini_header_label = tk.Label(
            mini_header,
            text=f"{self.year}年 {self.month}月",
            font=("Arial", 12, "bold"),
            bg="#1f77d4",
            fg="white",
        )
        self.mini_header_label.pack(pady=8)

        # 小カレンダー
        self.mini_cal = tk.Frame(left_panel, bg="white")
        self.mini_cal.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.create_mini_calendar()

        # タスク一覧セクション
        task_header = tk.Frame(left_panel, bg="#1f77d4")
        task_header.pack(fill=tk.X, pady=(10, 0))

        tk.Label(
            task_header,
            text="タスク一覧",
            font=("Arial", 12, "bold"),
            bg="#1f77d4",
            fg="white",
        ).pack(pady=8)

        # タスク一覧フレーム（スクロール対応）
        task_list_container = tk.Frame(left_panel, bg="white")
        task_list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # スクロールバー付きのタスク一覧
        scrollbar = tk.Scrollbar(task_list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_listbox = tk.Listbox(
            task_list_container,
            yscrollcommand=scrollbar.set,
            font=("Arial", 9),
            bg="white",
            relief=tk.FLAT,
            bd=0,
        )
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)

        # ダブルクリックでタスク削除
        self.task_listbox.bind("<Double-Button-1>", self.delete_task_from_listbox)

        # 右側パネル（メインカレンダー）
        right_panel = tk.Frame(main_container, bg="white", relief=tk.SOLID, bd=1)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # トップバー（月年と矢印）
        top_bar = tk.Frame(right_panel, bg="white")
        top_bar.pack(fill=tk.X, padx=15, pady=(10, 5))

        self.previous = tk.Label(top_bar, text="◀", font=("Arial", 16), bg="white")
        self.previous.bind("<1>", self.changeCal)
        self.previous.pack(side=tk.LEFT, padx=10)

        self.month_year_label = tk.Label(
            top_bar,
            text=f"{self.year}年 {self.month}月",
            font=("Arial", 18, "bold"),
            bg="white",
        )
        self.month_year_label.pack(side=tk.LEFT, expand=True)
        # 月年ラベルクリックで月選択ポップアップを開く
        self.month_year_label.bind("<1>", self.open_month_selector)

        self.next = tk.Label(top_bar, text="▶", font=("Arial", 16), bg="white")
        self.next.bind("<1>", self.changeCal)
        self.next.pack(side=tk.RIGHT, padx=10)

        # カレンダーグリッドコンテナ
        calendar_container = tk.Frame(right_panel, bg="white")
        calendar_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        # 曜日ヘッダー
        days_of_week = ["日", "月", "火", "水", "木", "金", "土"]
        colors = ["#ff6b6b", "black", "black", "black", "black", "black", "#4169e1"]

        header_frame = tk.Frame(calendar_container, bg="white")
        header_frame.pack(fill=tk.X, pady=(0, 8))

        for i, day in enumerate(days_of_week):
            tk.Label(
                header_frame,
                text=day,
                font=("Arial", 11, "bold"),
                fg=colors[i],
                bg="white",
                width=10,
            ).pack(side=tk.LEFT, expand=True)

        # 日付表示部分
        self.calDate = tk.Frame(calendar_container, bg="white")
        self.calDate.pack(fill=tk.BOTH, expand=True)

        # 日付部分を作成するメソッドの呼び出し
        self.createCal(self.year, self.month)
        self.update_task_listbox()

    # タスク一覧を更新
    def update_task_listbox(self):
        """タスク一覧ボックスを更新"""
        self.task_listbox.delete(0, tk.END)

        # 全タスクを日付順に表示
        for date_key, task in self.task_manager.all_tasks_sorted():
            display_text = f"[{date_key}] {task}"
            self.task_listbox.insert(tk.END, display_text)

    # リストボックスからタスクを削除
    def delete_task_from_listbox(self, event):
        """リストボックス内のタスクをダブルクリックで削除"""
        selection = self.task_listbox.curselection()
        if not selection:
            return

        # 選択されたテキストを取得
        selected_text = self.task_listbox.get(selection[0])

        # 日付とタスクを抽出 "[YYYY-MM-DD] task"
        try:
            date_key = selected_text.split("]")[0][1:]  # [の後から]の前まで
            task_name = selected_text.split("] ", 1)[1]  # ]の後のテキスト

            # 該当タスクを削除（名前一致の先頭を削除）
            tasks = self.task_manager.get_tasks(date_key)
            if task_name in tasks:
                idx = tasks.index(task_name)
                self.task_manager.remove_task_at(date_key, idx)
                self.update_task_listbox()
                self.createCal(self.year, self.month)
        except:
            pass

    # 小カレンダーを作成
    def create_mini_calendar(self):
        """左側の小カレンダーを作成"""
        # 曜日ヘッダー
        for i, day in enumerate(["日", "月", "火", "水", "木", "金", "土"]):
            tk.Label(self.mini_cal, text=day, font=("Arial", 8), width=3).grid(
                column=i, row=0, padx=1, pady=1
            )

        # カレンダーのデータを取得
        cal = calendar.Calendar()
        cal.setfirstweekday(6)
        days = cal.monthdayscalendar(self.year, self.month)

        # 日付を表示
        row = 1
        for week in days:
            for col, day in enumerate(week):
                if day != 0:
                    bg_color = "#e8f4f8" if day == self.today else "white"
                    label = tk.Label(
                        self.mini_cal,
                        text=str(day),
                        font=("Arial", 8),
                        width=3,
                        bg=bg_color,
                    )
                    label.grid(column=col, row=row, padx=1, pady=1)
                else:
                    tk.Label(self.mini_cal, text="", font=("Arial", 8), width=3).grid(
                        column=col, row=row, padx=1, pady=1
                    )
            row += 1

    # 日付キーを取得
    def get_date_key(self, year, month, day):
        return TaskManager.date_key(year, month, day)

    # タスクを追加
    def add_task(self, year, month, day):
        """指定された日付にタスクを追加"""
        task = simpledialog.askstring("タスク追加", "タスクを入力してください:")
        if task:
            date_key = self.get_date_key(year, month, day)
            self.task_manager.add_task(date_key, task)
            self.update_task_listbox()
            self.createCal(self.year, self.month)

    # タスクを削除
    def remove_task(self, year, month, day, task_index):
        """指定されたタスクを削除"""
        date_key = self.get_date_key(year, month, day)
        self.task_manager.remove_task_at(date_key, task_index)
        self.update_task_listbox()
        self.createCal(self.year, self.month)

    # 日付を表示
    def createCal(self, year, month):

        # 初期化：self.calDateの全ての子ウィジェットを破棄
        for widget in self.calDate.winfo_children():
            widget.destroy()

        self.day = {}

        cal = calendar.Calendar()
        cal.setfirstweekday(6)
        # 指定した年月のカレンダーをリストで返す
        days = cal.monthdayscalendar(year, month)

        self.day = {}
        # 日付
        for y in range(0, len(days)):
            week_frame = tk.Frame(self.calDate, bg="white")
            week_frame.pack(fill=tk.BOTH, pady=2)

            for x in range(0, 7):
                day_cell = tk.Frame(week_frame, bg="white", relief=tk.SOLID, bd=1)
                day_cell.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)

                if days[y][x] != 0:
                    date = days[y][x]

                    # 日付の色分け
                    if x == 6:  # 日曜日
                        text_color = "#ff6b6b"
                    elif x == 5:  # 土曜日
                        text_color = "#4169e1"
                    else:  # 平日
                        text_color = "black"

                    # 今日の日付をハイライト
                    if (
                        year == datetime.datetime.now().year
                        and month == datetime.datetime.now().month
                        and date == datetime.datetime.now().day
                    ):
                        bg_color = "#1f77d4"
                        text_color = "white"
                        font_style = ("Arial", 14, "bold")
                    else:
                        bg_color = "white"
                        font_style = ("Arial", 12, "bold")

                    # 内部フレーム
                    inner_frame = tk.Frame(day_cell, bg=bg_color)
                    inner_frame.pack(fill=tk.BOTH, expand=False)

                    # 日付ラベル
                    date_label = tk.Label(
                        inner_frame,
                        text=str(date),
                        font=font_style,
                        fg=text_color,
                        bg=bg_color,
                        padx=5,
                        pady=3,
                    )
                    date_label.pack(anchor=tk.NW)

                    # タスクを取得
                    date_key = self.get_date_key(year, month, date)
                    tasks = self.task_manager.get_tasks(date_key)

                    # タスク表示フレーム
                    if tasks:
                        task_frame = tk.Frame(inner_frame, bg=bg_color)
                        task_frame.pack(fill=tk.X, padx=3, pady=2)

                        for idx, task in enumerate(tasks[:2]):  # 最大2個表示
                            task_btn = tk.Label(
                                task_frame,
                                text=f"• {task[:15]}{'...' if len(task) > 15 else ''}",
                                font=("Arial", 8),
                                fg="#333" if bg_color == "white" else "white",
                                bg="#e8f4f8" if bg_color == "white" else "#0d5a99",
                                padx=2,
                                pady=2,
                                wraplength=80,
                                justify=tk.LEFT,
                            )
                            task_btn.pack(fill=tk.X, padx=1, pady=1)
                            # 詳細へ：クリックでタスク詳細ウィンドウ
                            task_btn.bind(
                                "<Button-1>",
                                lambda e, y=year, m=month, d=date, i=idx: self.open_task_detail(
                                    y, m, d, i
                                ),
                            )

                        if len(tasks) > 2:
                            more_label = tk.Label(
                                task_frame,
                                text=f"+{len(tasks) - 2}個",
                                font=("Arial", 7),
                                fg="#666" if bg_color == "white" else "#ccc",
                                bg=bg_color,
                            )
                            more_label.pack(anchor=tk.W, padx=2)

                    # タスク追加ボタン
                    add_btn = tk.Button(
                        inner_frame,
                        text="+ タスク",
                        font=("Arial", 8),
                        bg="#e8f4f8" if bg_color == "white" else "#0d5a99",
                        fg="#333" if bg_color == "white" else "white",
                        relief=tk.FLAT,
                        command=lambda y=year, m=month, d=date: self.add_task(y, m, d),
                    )
                    add_btn.pack(side=tk.LEFT, padx=2, pady=2)

                    # タスク管理ボタン
                    if tasks:
                        manage_btn = tk.Button(
                            inner_frame,
                            text="✓",
                            font=("Arial", 8),
                            bg="#e8f4f8" if bg_color == "white" else "#0d5a99",
                            fg="#333" if bg_color == "white" else "white",
                            relief=tk.FLAT,
                            width=3,
                            command=lambda y=year, m=month, d=date: self.manage_tasks(
                                y, m, d
                            ),
                        )
                        manage_btn.pack(side=tk.LEFT, padx=2, pady=2)

                    self.day[date] = day_cell
                else:
                    tk.Label(day_cell, text="", bg="#fafafa").pack(
                        fill=tk.BOTH, expand=True
                    )

    # タスク管理ウィンドウ
    def manage_tasks(self, year, month, day):
        """タスク管理用のポップアップウィンドウを表示"""
        date_key = self.get_date_key(year, month, day)
        tasks = self.task_manager.get_tasks(date_key)

        if not tasks:
            messagebox.showinfo("タスク", "この日付にはタスクがありません")
            return

        manage_window = tk.Toplevel()
        manage_window.title(f"{year}年{month}月{day}日のタスク")
        manage_window.geometry("300x300")

        # タスクリスト
        listbox = tk.Listbox(manage_window, height=10, width=40)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for task in tasks:
            listbox.insert(tk.END, task)

        # 削除ボタン
        def delete_selected():
            selection = listbox.curselection()
            if selection:
                self.remove_task(year, month, day, selection[0])
                manage_window.destroy()
            else:
                messagebox.showwarning("警告", "削除するタスクを選択してください")

        delete_btn = tk.Button(
            manage_window, text="削除", command=delete_selected, width=20
        )
        delete_btn.pack(pady=10)

        close_btn = tk.Button(
            manage_window, text="閉じる", command=manage_window.destroy, width=20
        )
        close_btn.pack(pady=5)

    # タスク詳細ウィンドウを開く
    def open_task_detail(self, year, month, day, task_index):
        date_key = self.get_date_key(year, month, day)
        tasks = self.tasks.get(date_key, [])
        if task_index < len(tasks):
            TaskDetailWindow(
                self,
                date_key,
                task_index,
                tasks[task_index],
                on_save=self.on_task_detail_save,
                on_delete=self.on_task_detail_delete,
            )

    # TaskDetailWindowからの保存コールバック
    def on_task_detail_save(self, date_key, task_index, new_text):
        self.task_manager.update_task_at(date_key, task_index, new_text)
        self.update_task_listbox()
        self.createCal(self.year, self.month)

    # TaskDetailWindowからの削除コールバック
    def on_task_detail_delete(self, date_key, task_index):
        self.task_manager.remove_task_at(date_key, task_index)
        self.update_task_listbox()
        self.createCal(self.year, self.month)

    #    # 年月を変更
    def changeCal(self, event):
        # 左右矢印のクリック判定をウィジェットの同一性で行う
        if event.widget is self.previous:
            self.month -= 1
            # 1になった場合
            if self.month == 0:
                self.year -= 1
                self.month = 12
        elif event.widget is self.next:
            self.month += 1
            # 13になった場合
            if self.month == 13:
                self.year += 1
                self.month = 1
        # month_year_labelクリックはopen_month_selectorにバインド済み

        # 年と月を変更
        self.month_year_label["text"] = f"{self.year}年 {self.month}月"
        # 左パネルのミニヘッダーも更新
        if hasattr(self, "mini_header_label"):
            self.mini_header_label["text"] = f"{self.year}年 {self.month}月"
        # 小カレンダーをリセット
        for widget in self.mini_cal.winfo_children():
            widget.destroy()
        self.create_mini_calendar()
        # 日付部分を作成する
        self.createCal(self.year, self.month)

    # 月選択ポップアップ
    def open_month_selector(self, event=None):
        selector = tk.Toplevel(self)
        selector.title("月を選択")
        selector.geometry("360x280")
        selector.transient(self.winfo_toplevel())
        selector.grab_set()

        # 年選択
        year_frame = tk.Frame(selector)
        year_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(year_frame, text="年", font=("Arial", 11)).pack(side=tk.LEFT)
        year_var = tk.IntVar(value=self.year)
        year_spin = tk.Spinbox(
            year_frame,
            from_=1970,
            to=2100,
            textvariable=year_var,
            width=6,
            font=("Arial", 11),
        )
        year_spin.pack(side=tk.LEFT, padx=8)
        tk.Button(
            year_frame,
            text="−",
            width=3,
            command=lambda: year_var.set(year_var.get() - 1),
        ).pack(side=tk.LEFT)
        tk.Button(
            year_frame,
            text="＋",
            width=3,
            command=lambda: year_var.set(year_var.get() + 1),
        ).pack(side=tk.LEFT)
        tk.Button(
            year_frame,
            text="今年",
            width=5,
            command=lambda: year_var.set(datetime.datetime.now().year),
        ).pack(side=tk.LEFT, padx=10)

        # 月選択グリッド
        month_var = tk.IntVar(value=self.month)
        grid = tk.Frame(selector)
        grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def set_month(m):
            month_var.set(m)
            # 簡易ハイライト更新
            for i, btn in enumerate(month_buttons, start=1):
                if i == m:
                    btn.configure(bg="#1f77d4", fg="white")
                else:
                    btn.configure(bg="#f0f0f0", fg="black")

        month_buttons = []
        names = [f"{i}月" for i in range(1, 13)]
        for idx, name in enumerate(names, start=1):
            r, c = divmod(idx - 1, 4)
            btn = tk.Button(
                grid,
                text=name,
                width=8,
                command=lambda m=idx: set_month(m),
                bg="#1f77d4" if idx == self.month else "#f0f0f0",
                fg="white" if idx == self.month else "black",
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            month_buttons.append(btn)
        for i in range(3):
            grid.rowconfigure(i, weight=1)
        for i in range(4):
            grid.columnconfigure(i, weight=1)

        # 操作ボタン
        action = tk.Frame(selector)
        action.pack(fill=tk.X, padx=10, pady=10)

        def apply_selection():
            self.year = int(year_var.get())
            self.month = int(month_var.get())
            # ヘッダー更新
            self.month_year_label["text"] = f"{self.year}年 {self.month}月"
            if hasattr(self, "mini_header_label"):
                self.mini_header_label["text"] = f"{self.year}年 {self.month}月"
            # ミニカレンダー再生成
            for w in self.mini_cal.winfo_children():
                w.destroy()
            self.create_mini_calendar()
            # メインカレンダー再生成
            self.createCal(self.year, self.month)
            selector.destroy()

        tk.Button(action, text="決定", width=10, command=apply_selection).pack(
            side=tk.RIGHT
        )
        tk.Button(action, text="キャンセル", width=10, command=selector.destroy).pack(
            side=tk.RIGHT, padx=6
        )


root = tk.Tk()
root.title("カレンダー")
root.geometry("1000x600")
root.configure(bg="#f5f5f5")

# 作成したウィジットを配置
widget = calWidget(root)
widget.pack(fill=tk.BOTH, expand=True)

root.mainloop()

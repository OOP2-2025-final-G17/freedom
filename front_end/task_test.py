# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os


class TaskManager:
    """タスクの永続化と操作を担当するクラス"""

    def __init__(self, task_file: str = "tasks.json") -> None:
        self.task_file = task_file
        self.tasks = {}  # {YYYY-MM-DD: [task, ...]}
        self.load()

    # 永続化
    def load(self) -> None:
        if os.path.exists(self.task_file):
            try:
                with open(self.task_file, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception:
                self.tasks = {}
        else:
            self.tasks = {}

    def save(self) -> None:
        with open(self.task_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    # ユーティリティ
    @staticmethod
    def date_key(year: int, month: int, day: int) -> str:
        return f"{year:04d}-{month:02d}-{day:02d}"

    # 取得系
    def get_tasks(self, date_key: str):
        return list(self.tasks.get(date_key, []))

    def all_tasks_sorted(self):
        for dk in sorted(self.tasks.keys()):
            for t in self.tasks[dk]:
                yield dk, t

    # 変更系
    def add_task(self, date_key: str, text: str) -> None:
        if not text:
            return
        self.tasks.setdefault(date_key, []).append(text)
        self.save()

    def remove_task_at(self, date_key: str, index: int) -> None:
        if date_key in self.tasks and 0 <= index < len(self.tasks[date_key]):
            self.tasks[date_key].pop(index)
            if not self.tasks[date_key]:
                del self.tasks[date_key]
            self.save()

    def update_task_at(self, date_key: str, index: int, new_text: str) -> None:
        if not new_text:
            return
        if date_key in self.tasks and 0 <= index < len(self.tasks[date_key]):
            self.tasks[date_key][index] = new_text
            self.save()


class TaskDetailWindow(tk.Toplevel):
    """タスク詳細ウィンドウ
    タスク編集・削除用のダイアログ。
    """

    def __init__(
        self,
        parent,
        date_key: str,
        task_index: int,
        task_text: str,
        on_save=None,
        on_delete=None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.date_key = date_key
        self.task_index = task_index
        self.task_text = task_text
        self.on_save_cb = on_save
        self.on_delete_cb = on_delete

        self.title(f"タスク詳細 - {date_key}")
        self.geometry("400x260")
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        # タイトル
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(header, text=date_key, font=("Arial", 12, "bold")).pack(anchor=tk.W)

        # 内容
        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        tk.Label(body, text="タスク内容", font=("Arial", 10)).pack(anchor=tk.W)

        self.text_var = tk.StringVar(value=self.task_text)
        self.entry = tk.Entry(body, textvariable=self.text_var, font=("Arial", 11))
        self.entry.pack(fill=tk.X, pady=6)

        # 操作ボタン
        actions = tk.Frame(self)
        actions.pack(fill=tk.X, padx=12, pady=10)

        tk.Button(actions, text="保存", width=10, command=self.on_save).pack(
            side=tk.RIGHT
        )
        tk.Button(actions, text="削除", width=10, command=self.on_delete).pack(
            side=tk.RIGHT, padx=6
        )
        tk.Button(actions, text="閉じる", width=10, command=self.destroy).pack(
            side=tk.LEFT
        )

    def on_save(self):
        new_text = self.text_var.get().strip()
        if not new_text:
            messagebox.showwarning("警告", "タスク内容を入力してください")
            return
        # コールバック経由で親に委譲
        if callable(self.on_save_cb):
            try:
                self.on_save_cb(self.date_key, self.task_index, new_text)
            finally:
                self.destroy()
        else:
            messagebox.showerror("エラー", "保存コールバックが設定されていません")

    def on_delete(self):
        if messagebox.askyesno("確認", "このタスクを削除しますか？"):
            if callable(self.on_delete_cb):
                try:
                    self.on_delete_cb(self.date_key, self.task_index)
                finally:
                    self.destroy()
            else:
                messagebox.showerror("エラー", "削除コールバックが設定されていません")

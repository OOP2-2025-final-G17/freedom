"""
データ I/O 処理モジュール
スケジュールデータのエクスポート/インポート機能を一元管理
"""

import os
import json
import datetime as dt
from tkinter import filedialog, messagebox

from ..request_handler import write_request, wait_for_response
from .constants import EXPORT_FOLDER_NAME, DEFAULT_TIMEOUT, IMPORT_TIMEOUT


def get_export_directory() -> str:
    """
    エクスポートディレクトリのパスを取得し、存在しなければ作成

    Returns:
        str: exportディレクトリの絶対パス
    """
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    export_dir = os.path.join(base_dir, EXPORT_FOLDER_NAME)
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def export_schedules(
    result_widget,
    master_root,
) -> bool:
    """
    全てのスケジュールをJSONファイルにエクスポート

    Args:
        result_widget: 結果表示用のテキストウィジェット（tk.Text）
        master_root: Tkinterのマスターウィンドウ

    Returns:
        bool: 成功したか否か
    """
    payload = {
        "action": "get_all_schedules",
    }
    request_id = write_request(payload)
    result_widget.delete("1.0", "end")
    result_widget.insert("end", "データをエクスポート中...\n")
    result_widget.update()

    resp = wait_for_response(
        "get_all_schedules",
        request_id,
        timeout=DEFAULT_TIMEOUT,
        root=master_root,
    )

    if resp and resp.get("ok") is True:
        data = resp.get("data", {})
        schedules = data.get("schedules", [])

        # エクスポートフォルダを取得
        export_dir = get_export_directory()

        # デフォルトのファイル名を生成
        default_filename = (
            f"schedules_export_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # ファイル保存ダイアログ
        file_path = filedialog.asksaveasfilename(
            title="エクスポート先を選択",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=export_dir,
            initialfile=default_filename,
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(schedules, f, ensure_ascii=False, indent=2)
                result_widget.insert(
                    "end", f"{len(schedules)}件の予定をエクスポートしました。\n"
                )
                result_widget.insert("end", f"保存先: {file_path}\n")
                messagebox.showinfo(
                    "成功", f"{len(schedules)}件の予定をエクスポートしました。"
                )
                return True
            except Exception as e:
                result_widget.insert("end", f"ファイル保存エラー: {e}\n")
                messagebox.showerror("エラー", f"ファイル保存に失敗しました: {e}")
                return False
        else:
            result_widget.insert("end", "エクスポートがキャンセルされました。\n")
            return False

    elif resp and resp.get("ok") is False:
        error = resp.get("error", {})
        result_widget.insert("end", f"エラー: {error.get('message', '不明なエラー')}\n")
        messagebox.showerror("エラー", error.get("message", "不明なエラー"))
        return False
    else:
        result_widget.insert(
            "end", "タイムアウト: バックエンドからの応答がありませんでした。\n"
        )
        messagebox.showerror("エラー", "バックエンドからの応答がありませんでした。")
        return False


def import_schedules(
    result_widget,
    master_root,
    on_success_callback=None,
) -> bool:
    """
    JSONファイルからスケジュールをインポート

    Args:
        result_widget: 結果表示用のテキストウィジェット（tk.Text）
        master_root: Tkinterのマスターウィンドウ
        on_success_callback: インポート成功時のコールバック関数（引数なし）

    Returns:
        bool: 成功したか否か
    """
    file_path = filedialog.askopenfilename(
        title="インポートするファイルを選択",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
    )

    if not file_path:
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            schedules = json.load(f)

        if not isinstance(schedules, list):
            messagebox.showerror(
                "エラー", "無効なファイル形式です。スケジュールのリストが必要です。"
            )
            return False

        # IDフィールドを削除（新規作成するため）
        for sc in schedules:
            if "id" in sc:
                del sc["id"]

        payload = {
            "action": "import_schedules",
            "schedules": schedules,
        }
        request_id = write_request(payload)
        result_widget.delete("1.0", "end")
        result_widget.insert("end", f"{len(schedules)}件の予定をインポート中...\n")
        result_widget.update()

        resp = wait_for_response(
            "import_schedules",
            request_id,
            timeout=IMPORT_TIMEOUT,
            root=master_root,
        )

        if resp and resp.get("ok") is True:
            data = resp.get("data", {})
            imported = data.get("imported", 0)
            errors = data.get("errors", [])

            result_widget.insert("end", f"{imported}件の予定をインポートしました。\n")
            if errors:
                result_widget.insert("end", f"{len(errors)}件のエラーがありました:\n")
                for err in errors[:10]:  # 最初の10件のみ表示
                    result_widget.insert("end", f"  - {err}\n")
                if len(errors) > 10:
                    result_widget.insert("end", f"  ... 他{len(errors) - 10}件\n")

            messagebox.showinfo("完了", f"{imported}件の予定をインポートしました。")

            # コールバック実行
            if on_success_callback:
                on_success_callback()

            return True

        elif resp and resp.get("ok") is False:
            error = resp.get("error", {})
            result_widget.insert(
                "end", f"エラー: {error.get('message', '不明なエラー')}\n"
            )
            messagebox.showerror("エラー", error.get("message", "不明なエラー"))
            return False
        else:
            result_widget.insert(
                "end", "タイムアウト: バックエンドからの応答がありませんでした。\n"
            )
            messagebox.showerror("エラー", "バックエンドからの応答がありませんでした。")
            return False

    except json.JSONDecodeError as e:
        messagebox.showerror("エラー", f"JSONファイルの解析に失敗しました: {e}")
        return False
    except Exception as e:
        messagebox.showerror("エラー", f"インポート中にエラーが発生しました: {e}")
        return False

"""
バリデーション関連の共通処理モジュール
日付、時刻、スケジュール形式などの検証を一元管理
"""

from datetime import datetime
from tkinter import messagebox


def validate_datetime_range(
    start_date_str: str,
    start_time_str: str,
    end_date_str: str,
    end_time_str: str,
) -> tuple[bool, str]:
    """
    開始日時と終了日時が有効な範囲かを検証

    Args:
        start_date_str: 開始日付（YYYY-MM-DD形式）
        start_time_str: 開始時刻（HH:MM形式）
        end_date_str: 終了日付（YYYY-MM-DD形式）
        end_time_str: 終了時刻（HH:MM形式）

    Returns:
        tuple[bool, str]: (検証成功/失敗, エラーメッセージ)
            成功時はメッセージは空文字列
    """
    try:
        start_dt = datetime.fromisoformat(f"{start_date_str}T{start_time_str}:00")
        end_dt = datetime.fromisoformat(f"{end_date_str}T{end_time_str}:00")

        # 同一日付で終了時刻が開始時刻より前
        if start_date_str == end_date_str and end_dt < start_dt:
            return False, "同じ日付のときは終了時刻は開始時刻より後にしてください。"

        # 終了が開始より前
        if end_dt < start_dt:
            return False, "終了日時は開始日時より後である必要があります。"

        return True, ""

    except ValueError:
        return (
            False,
            "日付と時刻の形式を確認してください。\n開始日: YYYY-MM-DD、時刻: HH:MM",
        )


def validate_schedule_format(
    name: str,
    mode: str,
    start_date_str: str,
    start_time_str: str,
    end_date_str: str,
    end_time_str: str,
) -> tuple[bool, str]:
    """
    スケジュール全体のバリデーション

    Args:
        name: スケジュール名
        mode: モード（A, B, NULL）
        start_date_str: 開始日付
        start_time_str: 開始時刻
        end_date_str: 終了日付
        end_time_str: 終了時刻

    Returns:
        tuple[bool, str]: (検証成功/失敗, エラーメッセージ)
    """
    # 名前が空かチェック
    if not name or not name.strip():
        return False, "タイトルを入力してください。"

    # 日付・時刻範囲のチェック
    is_valid, error_msg = validate_datetime_range(
        start_date_str, start_time_str, end_date_str, end_time_str
    )

    if not is_valid:
        return False, error_msg

    return True, ""


def parse_time_string(time_str: str) -> tuple[int, int] | None:
    """
    時刻文字列（HH:MM形式）をパース

    Args:
        time_str: 時刻文字列

    Returns:
        tuple[int, int] | None: (時, 分) または None（パース失敗時）
    """
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return None
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour < 24 and 0 <= minute < 60):
            return None
        return hour, minute
    except (ValueError, AttributeError):
        return None


def validate_month_year(year: int, month: int) -> tuple[bool, str]:
    """
    年月が有効かを検証

    Args:
        year: 年
        month: 月（1-12）

    Returns:
        tuple[bool, str]: (検証成功/失敗, エラーメッセージ)
    """
    if not (1 <= month <= 12):
        return False, "月は1-12で入力してください。"

    if year < 1900 or year > 2100:
        return False, "年は1900-2100で入力してください。"

    return True, ""


def validate_wage(wage: int) -> tuple[bool, str]:
    """
    時給が有効かを検証

    Args:
        wage: 時給（円）

    Returns:
        tuple[bool, str]: (検証成功/失敗, エラーメッセージ)
    """
    if wage < 0:
        return False, "時給は0以上で設定してください。"

    if wage > 100000:
        return False, "時給が高すぎます（100000円以上は設定不可）。"

    return True, ""

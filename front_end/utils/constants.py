"""
共通定数管理モジュール
給料計算、スケジュール管理などで使用する定数を一元管理
"""

# ================== 給料関連定数 ==================
DEFAULT_WAGE = 1000  # デフォルト時給（円）
NIGHT_RATE_MULTIPLIER = 1.25  # 深夜割増率（倍）

# 深夜時間帯の定義（24時間制）
NIGHT_HOURS_START = 22  # 深夜開始時刻（22時）
NIGHT_HOURS_END = 5  # 深夜終了時刻（5時）

# ================== スケジュール関連定数 ==================
SCHEDULE_MODES = {
    "A": "学校",
    "B": "バイト",
    "NULL": "その他",
}

DEFAULT_START_TIME = "09:00"
DEFAULT_END_TIME = "18:00"

# ================== ファイル・フォルダ関連定数 ==================
EXPORT_FOLDER_NAME = "export"
TASK_ID_FILE = "json/task_id.json"

# ================== UI関連定数 ==================
# ウィンドウサイズ
SALARY_WINDOW_WIDTH = 700
SALARY_WINDOW_HEIGHT = 600

CHANGE_WINDOW_WIDTH = 500
CHANGE_WINDOW_HEIGHT = 520

MONEY_WINDOW_WIDTH = 480
MONEY_WINDOW_HEIGHT = 420

# ================== タイムアウト設定 ==================
DEFAULT_TIMEOUT = 10.0  # デフォルトタイムアウト（秒）
IMPORT_TIMEOUT = 30.0  # インポート用タイムアウト（秒）

# ================== 日付・時刻フォーマット ==================
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
EXPORT_FILENAME_FORMAT = "schedules_export_%Y%m%d_%H%M%S"

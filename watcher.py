import json
from pathlib import Path

from PySide6.QtCore import QObject, QFileSystemWatcher, QTimer, Slot

from back_end.db.init import initialize_database
from back_end.functions import handle_request


REQUEST_PATH = Path("json/request.json")
RESPONSE_PATH = Path("json/response.json")


class JsonRequestWatcher(QObject):
    """
    json/request.json の変更を監視して、更新があったら
    handle_request(payload) を実行し json/response.json に保存する。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        initialize_database()

        self.watcher = QFileSystemWatcher(self)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._process_request)

        # 変更イベントが連続で飛ぶことがあるので、最後のイベントから少し待って処理
        self.debounce_ms = 120

        # request.json が存在しない場合に備える
        if not REQUEST_PATH.parent.exists():
            REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not REQUEST_PATH.exists():
            # 空の request.json を作る（とりあえず action なしで）
            REQUEST_PATH.write_text("{}", encoding="utf-8")

        self._add_watch_target()

        self.watcher.fileChanged.connect(self._on_file_changed)

    def _add_watch_target(self):
        # QFileSystemWatcher は、ファイルが置き換わると監視が外れることがあるため、
        # 監視対象が消えたら再登録する。
        paths = self.watcher.files()
        if str(REQUEST_PATH) not in paths:
            self.watcher.addPath(str(REQUEST_PATH))

    @Slot(str)
    def _on_file_changed(self, path: str):
        # 置き換え保存で監視が外れる場合があるので、毎回監視を張り直す
        self._add_watch_target()

        # debounce：保存途中で読み込むと壊れることがあるので少し待つ
        self.timer.start(self.debounce_ms)

    def _read_json_safely(self) -> dict:
        """
        書き込み途中で壊れたJSONを読んでしまうのを避けるため、
        失敗したら少し待って1回だけリトライする。
        """
        for i in range(2):
            try:
                text = REQUEST_PATH.read_text(encoding="utf-8")
                if not text.strip():
                    return {}
                return json.loads(text)
            except Exception:
                if i == 0:
                    # 1回だけ待って再挑戦
                    QTimer.singleShot(80, lambda: None)
                else:
                    return {"action": "unknown", "__parse_error__": True}
        return {}

    def _write_response(self, data: dict) -> None:
        if not RESPONSE_PATH.parent.exists():
            RESPONSE_PATH.parent.mkdir(parents=True, exist_ok=True)
        RESPONSE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _process_request(self):
        payload = self._read_json_safely()

        # JSONが壊れてた場合のレスポンス
        if isinstance(payload, dict) and payload.get("__parse_error__"):
            self._write_response({
                "ok": False,
                "action": "unknown",
                "error": {"code": "BAD_REQUEST", "message": "invalid json"}
            })
            return

        # action が無い request.json が来ることもあるので、その場合は何もしない/エラー返すは好み
        if not isinstance(payload, dict) or "action" not in payload:
            self._write_response({
                "ok": False,
                "action": "unknown",
                "error": {"code": "BAD_REQUEST", "message": "action is required"}
            })
            return

        result = handle_request(payload)
        self._write_response(result)

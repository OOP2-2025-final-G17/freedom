import json
from pathlib import Path

from back_end.db.init import initialize_database
from back_end.functions import handle_request

REQUEST_PATH = Path("json/request.json")
RESPONSE_PATH = Path("json/response.json")


class JsonRequestWatcherTk:
    """
    Tkinter の after() で request.json を監視し、
    変更があれば handle_request(payload) を実行して response.json に書く。
    """

    def __init__(self, tk_root, interval_ms: int = 200):
        self.root = tk_root
        self.interval_ms = interval_ms

        initialize_database()

        REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not REQUEST_PATH.exists():
            REQUEST_PATH.write_text("{}", encoding="utf-8")

        RESPONSE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not RESPONSE_PATH.exists():
            RESPONSE_PATH.write_text("{}", encoding="utf-8")

        self._last_mtime = self._get_mtime()
        self._scheduled = False

        # 監視開始
        self._tick()

    def _get_mtime(self) -> float:
        try:
            return REQUEST_PATH.stat().st_mtime
        except FileNotFoundError:
            return 0.0

    def _read_json_safely(self) -> dict:
        # 保存途中の一瞬で壊れることがあるので2回読む
        for _ in range(2):
            try:
                text = REQUEST_PATH.read_text(encoding="utf-8")
                if not text.strip():
                    return {}
                return json.loads(text)
            except Exception:
                # 少し待ってリトライ（Tkinterのafterで待つ都合上、ここは素直に続行）
                pass
        return {"__parse_error__": True}

    def _write_response(self, data: dict) -> None:
        RESPONSE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _process_request(self) -> None:
        payload = self._read_json_safely()

        if isinstance(payload, dict) and payload.get("__parse_error__"):
            self._write_response({
                "ok": False,
                "action": "unknown",
                "error": {"code": "BAD_REQUEST", "message": "invalid json"}
            })
            return

        if not isinstance(payload, dict) or "action" not in payload:
            self._write_response({
                "ok": False,
                "action": "unknown",
                "error": {"code": "BAD_REQUEST", "message": "action is required"}
            })
            return

        result = handle_request(payload)
        self._write_response(result)

    def _tick(self) -> None:
        mtime = self._get_mtime()

        # 変更検知
        if mtime != self._last_mtime:
            self._last_mtime = mtime

            # 連続保存対策：ちょい待ってから処理（debounce）
            if not self._scheduled:
                self._scheduled = True
                self.root.after(120, self._debounced_process)

        self.root.after(self.interval_ms, self._tick)

    def _debounced_process(self) -> None:
        self._scheduled = False
        self._process_request()

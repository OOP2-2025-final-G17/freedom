import json
from pathlib import Path

from back_end.db.init import initialize_database
from back_end.functions import handle_request

REQUEST_PATH = Path("json/request.json")
RESPONSE_PATH = Path("json/response.json")

# デバッグモード（False にするとログが出ない）
DEBUG = False


class JsonRequestWatcherTk:
    """
    Tkinter の after() で request.json を監視し、
    変更があれば handle_request(payload) を実行して response.json に書く。
    """

    def __init__(self, tk_root, interval_ms: int = 100):
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
        self._debounce_id = None

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
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _process_request(self) -> None:
        import time
        import sys
        from datetime import datetime

        try:
            print(
                f"[{datetime.now()}] _process_request started",
                file=sys.stderr,
                flush=True,
            )

            payload = self._read_json_safely()
            print(
                f"[{datetime.now()}] Payload read: {payload}",
                file=sys.stderr,
                flush=True,
            )

            if isinstance(payload, dict) and payload.get("__parse_error__"):
                print(
                    f"[{datetime.now()}] Parse error detected",
                    file=sys.stderr,
                    flush=True,
                )
                self._write_response(
                    {
                        "ok": False,
                        "action": "unknown",
                        "error": {"code": "BAD_REQUEST", "message": "invalid json"},
                    }
                )
                return

            if not isinstance(payload, dict) or "action" not in payload:
                print(
                    f"[{datetime.now()}] No action in payload, returning",
                    file=sys.stderr,
                    flush=True,
                )
                return  # 保存途中は無視（ここは好み）

            # リクエストIDを抽出（後でレスポンスに含める）
            request_id = payload.get("_request_id")
            print(
                f"[{datetime.now()}] Processing action: {payload.get('action')}, request_id: {request_id}",
                file=sys.stderr,
                flush=True,
            )

            result = handle_request(payload)
            print(
                f"[{datetime.now()}] handle_request returned: {result}",
                file=sys.stderr,
                flush=True,
            )

            # レスポンスにリクエストIDを含める
            if request_id:
                result["_request_id"] = request_id

            self._write_response(result)
            print(
                f"[{datetime.now()}] Response written successfully",
                file=sys.stderr,
                flush=True,
            )

        except Exception as e:
            import traceback

            print(f"[{datetime.now()}] Exception: {e}", file=sys.stderr, flush=True)
            print(traceback.format_exc(), file=sys.stderr, flush=True)
            # ★ここが重要：どんな例外でも response.json に出す
            self._write_response(
                {
                    "ok": False,
                    "action": "unknown",
                    "error": {"code": "EXCEPTION", "message": str(e)},
                }
            )

    def _tick(self) -> None:
        import sys
        from datetime import datetime

        mtime = self._get_mtime()

        # 変更検知
        if mtime != self._last_mtime:
            print(
                f"[{datetime.now()}] [_tick] File change detected! mtime: {mtime}, last: {self._last_mtime}",
                file=sys.stderr,
                flush=True,
            )
            self._last_mtime = mtime

            # 即座に処理（debounce は廃止）
            self._process_request()
        else:
            # ログを少なく出すため、変更がない場合はスキップ
            pass

        self.root.after(self.interval_ms, self._tick)

    def _debounced_process(self) -> None:
        import sys
        from datetime import datetime

        print(
            f"[{datetime.now()}] [_debounced_process] Started",
            file=sys.stderr,
            flush=True,
        )
        self._debounce_id = None
        self._process_request()

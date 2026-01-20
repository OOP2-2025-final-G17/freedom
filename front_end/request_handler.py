"""
リクエスト送信・レスポンス待機の共通モジュール
"""

import os
import json
import time
import uuid
from datetime import datetime


def _paths():
    """リクエスト・レスポンスファイルのパスを取得"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req = os.path.join(base, "json", "request.json")
    res = os.path.join(base, "json", "response.json")
    return req, res


def write_request(payload: dict) -> str:
    """
    リクエストを送信し、リクエストIDを返す

    Args:
        payload: リクエストペイロード（action等を含む辞書）

    Returns:
        str: 生成されたリクエストID
    """
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

    with open(req, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return request_id


def try_read_response() -> dict | None:
    """
    レスポンスファイルを読み込む（エラー時はNoneを返す）

    Returns:
        dict | None: レスポンスデータまたはNone
    """
    _, res = _paths()
    if not os.path.exists(res):
        return None
    try:
        with open(res, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def wait_for_response(
    expected_action: str,
    expected_request_id: str,
    expected_data_validator=None,
    timeout: float = 10.0,
    root=None,
    debug: bool = False,
) -> dict | None:
    """
    指定されたリクエストIDのレスポンスまで待機する

    Args:
        expected_action: 期待するアクション名
        expected_request_id: 期待するリクエストID
        expected_data_validator: データ検証用の関数（オプション）
        timeout: タイムアウト時間（秒）
        root: Tkinterのルートウィンドウ（イベントループ処理用）
        debug: デバッグログを出力するか

    Returns:
        dict | None: レスポンスデータまたはNone（タイムアウト時）
    """
    import sys

    _, res = _paths()
    start_time = time.time()

    if debug:
        print(
            f"[{datetime.now()}] wait_for_response started: action={expected_action}, request_id={expected_request_id}",
            file=sys.stderr,
            flush=True,
        )

    while time.time() - start_time < timeout:
        # Tkinter event loop を処理（バックエンドが実行されるようにする）
        if root:
            root.update()

        elapsed = time.time() - start_time

        # ファイルが存在するかチェック
        if not os.path.exists(res):
            if debug:
                print(
                    f"[{datetime.now()}] [{elapsed:.2f}s] Response file not found",
                    file=sys.stderr,
                    flush=True,
                )
            time.sleep(0.05)
            continue

        try:
            time.sleep(0.05)  # ファイル書き込み完了を待つ
            with open(res, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if debug:
                    print(
                        f"[{datetime.now()}] [{elapsed:.2f}s] Response content: {content[:100]}",
                        file=sys.stderr,
                        flush=True,
                    )

                if not content:  # 空ファイルの場合はスキップ
                    if debug:
                        print(
                            f"[{datetime.now()}] [{elapsed:.2f}s] Response file is empty",
                            file=sys.stderr,
                            flush=True,
                        )
                    time.sleep(0.05)
                    continue

                resp = json.loads(content)
                action = resp.get("action")
                request_id = resp.get("_request_id")

                if debug:
                    print(
                        f"[{datetime.now()}] [{elapsed:.2f}s] Parsed response: action={action}, request_id={request_id}",
                        file=sys.stderr,
                        flush=True,
                    )

                # 期待されるアクション＆リクエストIDのレスポンスか確認
                if action == expected_action and request_id == expected_request_id:
                    if debug:
                        print(
                            f"[{datetime.now()}] [{elapsed:.2f}s] Matching response found!",
                            file=sys.stderr,
                            flush=True,
                        )

                    # 追加の検証があればチェック
                    if expected_data_validator is None or expected_data_validator(resp):
                        return resp
                    else:
                        # 検証失敗：異なるデータの場合は待機を続ける
                        if debug:
                            print(
                                f"[{datetime.now()}] [{elapsed:.2f}s] Validator failed",
                                file=sys.stderr,
                                flush=True,
                            )
                        time.sleep(0.05)
                else:
                    # 異なるリクエストIDまたはアクションの場合は無視して待機を続ける
                    if debug:
                        print(
                            f"[{datetime.now()}] [{elapsed:.2f}s] Not matching (expected action={expected_action}, request_id={expected_request_id})",
                            file=sys.stderr,
                            flush=True,
                        )
                    time.sleep(0.05)

        except (json.JSONDecodeError, IOError) as e:
            # JSONパースエラーまたはファイル読み込みエラーは無視して再試行
            if debug:
                print(
                    f"[{datetime.now()}] [{elapsed:.2f}s] Error reading response: {e}",
                    file=sys.stderr,
                    flush=True,
                )
            time.sleep(0.05)
            continue

    if debug:
        print(
            f"[{datetime.now()}] wait_for_response timeout!",
            file=sys.stderr,
            flush=True,
        )

    return None

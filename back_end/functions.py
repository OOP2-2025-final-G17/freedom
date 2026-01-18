from datetime import datetime, date, time
from typing import Dict, Any, List, cast

from back_end.db.db import db, Schedule


def ok(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {"ok": True, "action": action, "data": data}


def ng(action: str, code: str, message: str) -> Dict[str, Any]:
    return {"ok": False, "action": action, "error": {"code": code, "message": message}}


def schedule_to_dict(s: Schedule) -> Dict[str, Any]:
    # Peeweeのフィールドを明示的にPythonの型として扱う
    start_date = cast(date, s.start_date)
    start_time = cast(time, s.start_time)
    end_date = cast(date, s.end_date)
    end_time = cast(time, s.end_time)
    
    return {
        "id": s.id,
        "mode": s.mode,
        "name": s.name,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "start_time": start_time.strftime("%H:%M"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "end_time": end_time.strftime("%H:%M"),
    }


def add_schedule(payload: dict) -> dict:
    action = "add_schedule"

    try:
        sd = datetime.strptime(payload["start_date"], "%Y-%m-%d").date()
        st = datetime.strptime(payload["start_time"], "%H:%M").time()
        ed = datetime.strptime(payload["end_date"], "%Y-%m-%d").date()
        et = datetime.strptime(payload["end_time"], "%H:%M").time()
    except Exception:
        return ng(action, "BAD_REQUEST", "invalid date/time format")

    if datetime.combine(ed, et) <= datetime.combine(sd, st):
        return ng(action, "VALIDATION_ERROR", "end must be after start")

    db.connect(reuse_if_open=True)
    with db.atomic():
        s = Schedule.create(
            mode=payload.get("mode"),
            name=payload.get("name"),
            start_date=sd,
            start_time=st,
            end_date=ed,
            end_time=et,
        )

    return ok(action, {"schedule": schedule_to_dict(s)})


def get_schedule(payload: dict) -> dict:
    action = "get_schedule"

    if "date" not in payload:
        return ng(action, "BAD_REQUEST", "date required")

    try:
        target_date = datetime.strptime(payload["date"], "%Y-%m-%d").date()
    except Exception:
        return ng(action, "BAD_REQUEST", "invalid date format")

    db.connect(reuse_if_open=True)

    query = (
        Schedule.select()
        .where(
            (Schedule.start_date <= target_date) & (Schedule.end_date >= target_date)
        )
        .order_by(Schedule.start_time)
    )

    return ok(
        action,
        {"date": payload["date"], "schedules": [schedule_to_dict(s) for s in query]},
    )


def delete_schedule(payload: dict) -> dict:
    action = "delete_schedule"

    if "id" not in payload:
        return ng(action, "BAD_REQUEST", "id required")

    db.connect(reuse_if_open=True)

    s = Schedule.get_or_none(Schedule.id == payload["id"])
    if not s:
        return ng(action, "NOT_FOUND", "schedule not found")

    s.delete_instance()
    return ok(action, {"deleted": payload["id"]})


def update_schedule(payload: dict) -> dict:
    action = "update_schedule"

    if "id" not in payload:
        return ng(action, "BAD_REQUEST", "id required")

    try:
        schedule_id = int(payload["id"])
    except Exception:
        return ng(action, "BAD_REQUEST", "id must be int")

    try:
        sd = datetime.strptime(payload["start_date"], "%Y-%m-%d").date()
        st = datetime.strptime(payload["start_time"], "%H:%M").time()
        ed = datetime.strptime(payload["end_date"], "%Y-%m-%d").date()
        et = datetime.strptime(payload["end_time"], "%H:%M").time()
    except Exception:
        return ng(action, "BAD_REQUEST", "invalid date/time format")

    if datetime.combine(ed, et) <= datetime.combine(sd, st):
        return ng(action, "VALIDATION_ERROR", "end must be after start")

    db.connect(reuse_if_open=True)

    s = Schedule.get_or_none(Schedule.id == schedule_id)
    if not s:
        return ng(action, "NOT_FOUND", "schedule not found")

    with db.atomic():
        s.mode = payload.get("mode")
        s.name = payload.get("name")
        s.start_date = sd
        s.start_time = st
        s.end_date = ed
        s.end_time = et
        s.save()

    return ok(action, {"schedule": schedule_to_dict(s)})


def get_monthly_schedule_by_mode(payload: dict) -> dict:
    action = "get_monthly_schedule_by_mode"

    if "year" not in payload or "month" not in payload:
        return ng(action, "BAD_REQUEST", "year and month required")

    try:
        year = int(payload["year"])
        month = int(payload["month"])
    except Exception:
        return ng(action, "BAD_REQUEST", "invalid year or month format")

    if month < 1 or month > 12:
        return ng(action, "BAD_REQUEST", "month must be between 1 and 12")

    mode = payload.get("mode", "B")  # デフォルトはB

    db.connect(reuse_if_open=True)

    # 月の最初の日と最後の日を計算
    import calendar

    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    # 指定された月に含まれるスケジュールを取得
    query = (
        Schedule.select()
        .where(
            (Schedule.mode == mode)
            & (
                # スケジュールが月の範囲内に含まれる
                ((Schedule.start_date <= last_day) & (Schedule.end_date >= first_day))
            )
        )
        .order_by(Schedule.start_date, Schedule.start_time)
    )

    return ok(
        action,
        {
            "year": year,
            "month": month,
            "mode": mode,
            "schedules": [schedule_to_dict(s) for s in query],
        },
    )


def get_monthly_schedule(payload: dict) -> dict:
    """月全体の予定を取得（モード指定なし）"""
    action = "get_monthly_schedule"

    if "year" not in payload or "month" not in payload:
        return ng(action, "BAD_REQUEST", "year and month required")

    try:
        year = int(payload["year"])
        month = int(payload["month"])
    except Exception:
        return ng(action, "BAD_REQUEST", "invalid year or month format")

    if month < 1 or month > 12:
        return ng(action, "BAD_REQUEST", "month must be between 1 and 12")

    db.connect(reuse_if_open=True)

    # 月の最初の日と最後の日を計算
    import calendar

    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    # 指定された月に含まれる全てのスケジュールを取得
    query = (
        Schedule.select()
        .where((Schedule.start_date <= last_day) & (Schedule.end_date >= first_day))
        .order_by(Schedule.start_date, Schedule.start_time)
    )

    return ok(
        action,
        {
            "year": year,
            "month": month,
            "schedules": [schedule_to_dict(s) for s in query],
        },
    )


def get_all_schedules(payload: dict) -> dict:
    """全ての予定を取得（エクスポート用）"""
    action = "get_all_schedules"

    db.connect(reuse_if_open=True)

    query = Schedule.select().order_by(Schedule.start_date, Schedule.start_time)

    return ok(
        action,
        {
            "schedules": [schedule_to_dict(s) for s in query],
        },
    )


def import_schedules(payload: dict) -> dict:
    """スケジュールをインポート"""
    action = "import_schedules"

    if "schedules" not in payload:
        return ng(action, "BAD_REQUEST", "schedules required")

    schedules = payload["schedules"]
    if not isinstance(schedules, list):
        return ng(action, "BAD_REQUEST", "schedules must be a list")

    db.connect(reuse_if_open=True)

    imported_count = 0
    errors = []

    with db.atomic():
        for idx, sc in enumerate(schedules):
            try:
                sd = datetime.strptime(sc["start_date"], "%Y-%m-%d").date()
                st = datetime.strptime(sc["start_time"], "%H:%M").time()
                ed = datetime.strptime(sc["end_date"], "%Y-%m-%d").date()
                et = datetime.strptime(sc["end_time"], "%H:%M").time()

                if datetime.combine(ed, et) <= datetime.combine(sd, st):
                    errors.append(f"Index {idx}: end must be after start")
                    continue

                Schedule.create(
                    mode=sc.get("mode"),
                    name=sc.get("name"),
                    start_date=sd,
                    start_time=st,
                    end_date=ed,
                    end_time=et,
                )
                imported_count += 1

            except Exception as e:
                errors.append(f"Index {idx}: {str(e)}")
                continue

    return ok(
        action,
        {
            "imported": imported_count,
            "errors": errors,
        },
    )


def handle_request(payload: dict) -> dict:
    action = payload.get("action")

    if action == "add_schedule":
        return add_schedule(payload)
    if action == "get_schedule":
        return get_schedule(payload)
    if action == "delete_schedule":
        return delete_schedule(payload)
    if action == "update_schedule":
        return update_schedule(payload)
    if action == "get_monthly_schedule_by_mode":
        return get_monthly_schedule_by_mode(payload)
    if action == "get_monthly_schedule":
        return get_monthly_schedule(payload)
    if action == "get_all_schedules":
        return get_all_schedules(payload)
    if action == "import_schedules":
        return import_schedules(payload)

    return ng(action or "unknown", "BAD_REQUEST", "unsupported action")

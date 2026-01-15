from datetime import datetime
from typing import Dict, Any

from back_end.db.db import db, Schedule


def ok(action: str, data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "action": action,
        "data": data
    }


def ng(action: str, code: str, message: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "action": action,
        "error": {
            "code": code,
            "message": message
        }
    }


def schedule_to_dict(s: Schedule) -> Dict[str, Any]:
    return {
        "id": s.id,
        "mode": s.mode,
        "name": s.name,
        "start_date": s.start_date.strftime("%Y-%m-%d"),
        "start_time": s.start_time.strftime("%H:%M"),
        "end_date": s.end_date.strftime("%Y-%m-%d"),
        "end_time": s.end_time.strftime("%H:%M"),
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
        Schedule
        .select()
        .where(
            (Schedule.start_date <= target_date) &
            (Schedule.end_date >= target_date)
        )
        .order_by(Schedule.start_time)
    )

    return ok(
        action,
        {
            "date": payload["date"],
            "schedules": [schedule_to_dict(s) for s in query]
        }
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

    return ng(action or "unknown", "BAD_REQUEST", "unsupported action")


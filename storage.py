"""Small, dependency-free storage and reminder domain helpers.

The app is intentionally offline-first. JSON remains the portable format, but
all writes are atomic and every reminder has a stable id (never a list index).
"""
import json
import os
import shutil
import tempfile
import uuid
from datetime import date, datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")
TRACK_FILE = os.path.join(DATA_DIR, "tracker.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def read_json(path, default):
    ensure_data_dir()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            value = json.load(fh)
        return value
    except (OSError, json.JSONDecodeError, TypeError):
        return default

def write_json_atomic(path, value):
    ensure_data_dir()
    folder = os.path.dirname(path) or "."
    fd, temporary = tempfile.mkstemp(prefix=".medicine-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(value, fh, indent=2, ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)

def backup_data():
    ensure_data_dir()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = os.path.join(DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    for source in (REMINDERS_FILE, TRACK_FILE, SETTINGS_FILE):
        if os.path.exists(source):
            shutil.copy2(source, os.path.join(backup_dir, f"{stamp}-{os.path.basename(source)}"))

def load_reminders():
    reminders = read_json(REMINDERS_FILE, [])
    changed = False
    normalized = []
    for item in reminders if isinstance(reminders, list) else []:
        if not isinstance(item, dict):
            continue
        item = dict(item)
        if not item.get("id"):
            item["id"] = uuid.uuid4().hex
            changed = True
        item.setdefault("frequency", "once")
        item.setdefault("weekdays", [])
        item.setdefault("dosage", "")
        item.setdefault("unit", "tablet")
        item.setdefault("instructions", "")
        item.setdefault("quantity", "")
        item.setdefault("refill_threshold", "")
        item.setdefault("active", True)
        normalized.append(item)
    if changed:
        write_json_atomic(REMINDERS_FILE, normalized)
    return normalized

def save_reminders(reminders):
    backup_data()
    write_json_atomic(REMINDERS_FILE, reminders)

def load_tracker():
    value = read_json(TRACK_FILE, {})
    return value if isinstance(value, dict) else {}

def save_tracker(value):
    write_json_atomic(TRACK_FILE, value)

def load_settings():
    defaults = {"sound": True, "vibration": True, "notifications": True,
                "dark_mode": False, "tts": False, "high_contrast": False,
                "grace_period_minutes": 120}
    value = read_json(SETTINGS_FILE, {})
    if isinstance(value, dict):
        defaults.update(value)
    return defaults

def save_settings(value):
    write_json_atomic(SETTINGS_FILE, value)

def validate_reminder(item):
    errors = []
    medicine = str(item.get("medicine", "")).strip()
    if not medicine or len(medicine) > 100:
        errors.append("Medication name is required and must be 100 characters or fewer.")
    try:
        datetime.strptime(str(item.get("date", "")), "%Y-%m-%d")
    except ValueError:
        errors.append("Use a valid date in YYYY-MM-DD format.")
    try:
        datetime.strptime(str(item.get("time", "")), "%I:%M %p")
    except ValueError:
        errors.append("Use a valid time such as 08:30 AM.")
    frequency = item.get("frequency", "once")
    if frequency not in ("once", "daily", "weekly"):
        errors.append("Frequency must be once, daily, or weekly.")
    if frequency == "weekly" and not item.get("weekdays"):
        errors.append("Select at least one weekday for a weekly schedule.")
    return errors

def reminder_occurs_on(reminder, day):
    if not reminder.get("active", True):
        return False
    try:
        start = datetime.strptime(reminder["date"], "%Y-%m-%d").date()
    except (KeyError, ValueError):
        return False
    end_text = reminder.get("end_date") or ""
    if day < start or (end_text and day > datetime.strptime(end_text, "%Y-%m-%d").date()):
        return False
    frequency = reminder.get("frequency", "once")
    return frequency == "daily" or (frequency == "weekly" and WEEKDAYS[day.weekday()] in reminder.get("weekdays", [])) or (frequency == "once" and day == start)

def event_key(reminder_id, day, time_text):
    return f"{reminder_id}:{day.isoformat()}:{time_text}"

def occurrence_datetime(reminder, day):
    return datetime.strptime(f"{day.isoformat()} {reminder['time']}", "%Y-%m-%d %I:%M %p")

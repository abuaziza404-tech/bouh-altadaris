# BOUH GOLD EXPLORER
# Full integrated prototype for gold target discovery and surface prospecting
# Developer: Ahmed Abu Aziza
# Version: 1.0

import hashlib
import json
import math
import os
import sqlite3
import time
from typing import Dict, Iterable, List, Tuple

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

APP_NAME = "BOUH Gold Explorer"
APP_VERSION = "1.0"
DEVELOPER = "Ahmed Abu Aziza"
DATA_DIR = os.path.join(os.path.expanduser("~"), "BOUH_GOLD_EXPLORER")
DB_PATH = os.path.join(DATA_DIR, "bouh_gold_explorer.db")


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def init_db():
    ensure_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS targets (
            id TEXT PRIMARY KEY,
            ts INTEGER,
            lat REAL,
            lon REAL,
            score REAL,
            level TEXT,
            decision TEXT,
            reasons TEXT,
            note TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analogs (
            id TEXT PRIMARY KEY,
            name TEXT,
            lat REAL,
            lon REAL,
            weight REAL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO analogs (id, name, lat, lon, weight) VALUES (?, ?, ?, ?, ?)",
        ("A1", "Dark Regolith Analog", 19.8200, 36.5400, 0.92),
    )
    conn.execute(
        "INSERT OR IGNORE INTO analogs (id, name, lat, lon, weight) VALUES (?, ?, ?, ?, ?)",
        ("A2", "Wadi Contact Analog", 20.4500, 36.3500, 0.88),
    )
    conn.execute(
        "INSERT OR IGNORE INTO analogs (id, name, lat, lon, weight) VALUES (?, ?, ?, ?, ?)",
        ("A3", "Quartz Ridge Analog", 20.7000, 36.4200, 0.80),
    )
    conn.execute(
        "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
        ("threshold", "70"),
    )
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def to_score(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def analyze_target(lat: float, lon: float, indicators: Dict[str, int], note: str = "") -> Dict[str, object]:
    # Baseline numeric model for surface gold detection.
    # This is a starter model intended for field screening, not a definitive assay.
    inferred = {
        "structure": to_score(indicators.get("structure", 0)),
        "quartz": to_score(indicators.get("quartz", 0)),
        "clay": to_score(indicators.get("clay", 0)),
        "wadi": to_score(indicators.get("wadi", 0)),
        "dark_regolith": to_score(indicators.get("dark_regolith", 0)),
        "old_work": to_score(indicators.get("old_work", 0)),
        "gpz_repeat": to_score(indicators.get("gpz_repeat", 0)),
        "fault": to_score(indicators.get("fault", 0)),
        "silica": to_score(indicators.get("silica", 0)),
    }

    # rough analog proximity scoring
    analog_best = 0.0
    analog_name = "none"
    conn = get_db()
    rows = conn.execute("SELECT name, lat, lon, weight FROM analogs").fetchall()
    conn.close()
    for row in rows:
        d = haversine_km(lat, lon, row["lat"], row["lon"])
        if d < 15.0:
            score = max(0.0, (15.0 - d) / 15.0) * float(row["weight"]) * 100.0
            if score > analog_best:
                analog_best = score
                analog_name = row["name"]

    # weights
    score = 0.0
    reasons: List[str] = []

    if inferred["structure"]:
        score += 24
        reasons.append("structure")
    if inferred["fault"]:
        score += 17
        reasons.append("fault_zone")
    if inferred["quartz"]:
        score += 16
        reasons.append("quartz")
    if inferred["silica"]:
        score += 14
        reasons.append("silica_high")
    if inferred["clay"]:
        score += 14
        reasons.append("clay")
    if inferred["wadi"]:
        score += 8
        reasons.append("wadi")
    if inferred["dark_regolith"]:
        score += 10
        reasons.append("dark_regolith")
    if inferred["old_work"]:
        score += 12
        reasons.append("old_work")
    if inferred["gpz_repeat"]:
        score += 15
        reasons.append("gpz_repeat")

    score += analog_best * 0.35
    if analog_name != "none":
        reasons.append(f"analog={analog_name}")

    score = min(score, 100.0)

    # rules
    if score >= 85 and (inferred["quartz"] or inferred["silica"] or inferred["fault"]):
        level = "Priority 1"
        decision = "Field priority: strong surface indicator"
    elif score >= 70:
        level = "Candidate"
        decision = "Field verification required"
    elif score >= 55:
        level = "Monitoring"
        decision = "Low priority; continue observation"
    else:
        level = "Low"
        decision = "No strong indicator"

    return {
        "id": hashlib.sha1(f"{time.time_ns()}:{lat}:{lon}".encode()).hexdigest()[:12],
        "ts": int(time.time() * 1000),
        "lat": float(lat),
        "lon": float(lon),
        "score": round(score, 2),
        "level": level,
        "decision": decision,
        "reasons": ", ".join(reasons) if reasons else "no clear signal",
        "note": note or "No note",
    }


def save_target(payload: Dict[str, object]):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO targets (id, ts, lat, lon, score, level, decision, reasons, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            payload["id"],
            payload["ts"],
            payload["lat"],
            payload["lon"],
            payload["score"],
            payload["level"],
            payload["decision"],
            payload["reasons"],
            payload["note"],
        ),
    )
    conn.commit()
    conn.close()


def get_recent_targets(limit: int = 10) -> List[sqlite3.Row]:
    conn = get_db()
    rows = conn.execute("SELECT * FROM targets ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return rows


class CheckRow(BoxLayout):
    def __init__(self, label: str, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(36), **kwargs)
        self.label = Label(text=label, size_hint_x=0.7)
        self.check = CheckBox(active=False, size_hint_x=0.3)
        self.add_widget(self.label)
        self.add_widget(self.check)

    def checked(self):
        return 1 if self.check.active else 0


class TargetApp(App):
    def build(self):
        init_db()
        root = BoxLayout(orientation="vertical", padding=10, spacing=8)

        title = Label(text="BOUH GOLD EXPLORER", font_size=24, bold=True, color=(0.85, 0.72, 0.29, 1), size_hint_y=None, height=dp(40))
        root.add_widget(title)

        form = GridLayout(cols=2, spacing=8, size_hint_y=None, height=dp(120))
        form.add_widget(Label(text="Latitude"))
        self.lat_box = TextInput(text="19.8500", multiline=False)
        form.add_widget(self.lat_box)
        form.add_widget(Label(text="Longitude"))
        self.lon_box = TextInput(text="36.8500", multiline=False)
        form.add_widget(self.lon_box)
        root.add_widget(form)

        checks = GridLayout(cols=2, spacing=6, size_hint_y=None, height=dp(200))
        self.checks = {
            "structure": CheckRow("Structure"),
            "fault": CheckRow("Fault / contact"),
            "quartz": CheckRow("Quartz"),
            "silica": CheckRow("Silica"),
            "clay": CheckRow("Clay / alteration"),
            "wadi": CheckRow("Wadi / drainage"),
            "dark_regolith": CheckRow("Dark regolith"),
            "old_work": CheckRow("Old artisanal work"),
            "gpz_repeat": CheckRow("Repeated GPZ signal"),
        }
        for key in self.checks:
            checks.add_widget(self.checks[key])
        root.add_widget(checks)

        note_box = TextInput(hint_text="Field note (quartz, red rock, wadi, etc)", size_hint_y=None, height=dp(80), multiline=True)
        root.add_widget(note_box)

        action_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=8)
        analyze_btn = Button(text="Analyze target")
        analyze_btn.bind(on_release=lambda *_: self.run_analysis(note_box.text))
        action_row.add_widget(analyze_btn)

        clear_btn = Button(text="Clear")
        clear_btn.bind(on_release=lambda *_: self.clear_view())
        action_row.add_widget(clear_btn)
        root.add_widget(action_row)

        self.result_label = Label(text="Result: waiting", size_hint_y=None, height=dp(110), halign="left", valign="top")
        root.add_widget(self.result_label)

        self.history = Label(text="Recent targets: none", size_hint_y=None, height=dp(160), halign="left", valign="top")
        root.add_widget(self.history)

        self.refresh_history()
        return root

    def clear_view(self):
        self.result_label.text = "Result: waiting"
        self.lat_box.text = "19.8500"
        self.lon_box.text = "36.8500"
        for obj in self.checks.values():
            obj.check.active = False

    def run_analysis(self, note: str):
        try:
            lat = float(self.lat_box.text)
            lon = float(self.lon_box.text)
        except ValueError:
            self.result_label.text = "Please enter valid coordinates."
            return

        indicators = {k: 1 if v.check.active else 0 for k, v in self.checks.items()}
        result = analyze_target(lat, lon, indicators, note)
        save_target(result)
        self.result_label.text = (
            f"ID: {result['id']}\n"
            f"Score: {result['score']}\n"
            f"Level: {result['level']}\n"
            f"Decision: {result['decision']}\n"
            f"Reasons: {result['reasons']}\n"
            f"Note: {result['note']}"
        )
        self.refresh_history()

    def refresh_history(self):
        rows = get_recent_targets(5)
        if not rows:
            self.history.text = "Recent targets: none"
            return
        lines = ["Recent targets:"]
        for row in rows:
            lines.append(
                f"{row['level']} | score={row['score']} | lat={row['lat']:.4f} | lon={row['lon']:.4f} | {row['decision']}"
            )
        self.history.text = "\n".join(lines)


if __name__ == "__main__":
    TargetApp().run()

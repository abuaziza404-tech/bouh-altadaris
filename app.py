# app.py
# BOUH Terrain | Abu Aziza System V5
# Python Native / Kivy / Offline-first / No npm / No Expo
# Developer: Ahmed Abu Aziza

import os
import math
import json
import time
import sqlite3
import hashlib
import binascii
import threading
import urllib.request
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup

try:
    from plyer import gps, compass, accelerometer, filechooser
except Exception:
    gps = None
    compass = None
    accelerometer = None
    filechooser = None


APP_NAME = "بوح التضاريس | منظومة ابوعزيزه"
APP_NAME_EN = "BOUH Terrain | Abu Aziza System"
DEVELOPER = "Ahmed Abu Aziza"
PACKAGE = "com.abuaziza.bouhgoldpro"
TARGET_EMAIL = "Abuaziza404@gmail.com"

DATA_DIR = os.path.join(os.path.expanduser("~"), "BOUH_DATA")
DB_PATH = os.path.join(DATA_DIR, "bouh_v5.sqlite")
QUEUE_PATH = os.path.join(DATA_DIR, "mail_queue.jsonl")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

# Android external app-data path note:
# On Android this maps effectively under app sandbox; copy packages to:
# /Android/data/com.abuaziza.bouhgoldpro/files/BOUH_DATA/
# For Kivy/Python portable path, the app creates ~/BOUH_DATA in its sandbox.


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "mbtiles"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "terrain_rgb"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "spectral"), exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "imports"), exist_ok=True)


def now_ms() -> int:
    return int(time.time() * 1000)


def fnum(x, nd=6) -> str:
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return "0.000000"


def pct(x) -> str:
    try:
        return f"{float(x):.2f}%"
    except Exception:
        return "0.00%"


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing_deg(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def terrain_rgb_elevation(r: int, g: int, b: int) -> float:
    return -10000.0 + ((r * 256 * 256 + g * 256 + b) * 0.1)


def pbkdf2_key(password: str, salt: bytes, iterations: int = 240000) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)


def pseudo_encrypt_text(text: str, password: str) -> str:
    # Practical fallback without external crypto package:
    # PBKDF2-derived XOR stream. For production replace with SQLCipher/AES-256.
    salt = os.urandom(16)
    key = pbkdf2_key(password, salt)
    raw = text.encode("utf-8")
    stream = hashlib.sha256(key + salt).digest()
    out = bytearray()
    for i, b in enumerate(raw):
        if i % len(stream) == 0:
            stream = hashlib.sha256(stream + key + i.to_bytes(8, "little")).digest()
        out.append(b ^ stream[i % len(stream)])
    return binascii.hexlify(salt + bytes(out)).decode("ascii")


def pseudo_decrypt_text(hex_text: str, password: str) -> str:
    buf = binascii.unhexlify(hex_text.encode("ascii"))
    salt, enc = buf[:16], buf[16:]
    key = pbkdf2_key(password, salt)
    stream = hashlib.sha256(key + salt).digest()
    out = bytearray()
    for i, b in enumerate(enc):
        if i % len(stream) == 0:
            stream = hashlib.sha256(stream + key + i.to_bytes(8, "little")).digest()
        out.append(b ^ stream[i % len(stream)])
    return out.decode("utf-8")


@dataclass
class SpectralPixel:
    b2: float = 0.0
    b4: float = 0.0
    b6: float = 0.0
    b7: float = 0.0
    silica: float = 0.0
    lineament_density: float = 0.0
    shear_intersection: float = 0.0
    elevation: float = 0.0
    source: str = "no_raw_pixel"


class BouhDatabase:
    def __init__(self, path=DB_PATH):
        ensure_dirs()
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()
        self.seed_reference_data()

    def init_schema(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS targets(
            id TEXT PRIMARY KEY,
            ts INTEGER,
            lat REAL,
            lon REAL,
            score REAL,
            cls TEXT,
            decision TEXT,
            clay REAL,
            iron REAL,
            silica REAL,
            lineament REAL,
            elevation REAL,
            distance_klemm_km REAL,
            nearest_klemm TEXT,
            reasons TEXT,
            note TEXT,
            synced INTEGER DEFAULT 0
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS klemm_sites(
            id TEXT PRIMARY KEY,
            name TEXT,
            lat REAL,
            lon REAL,
            group_name TEXT,
            lithology TEXT,
            structure TEXT,
            alteration TEXT,
            analog_class TEXT,
            reliability INTEGER
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS analogs(
            id TEXT PRIMARY KEY,
            lat REAL,
            lon REAL,
            kind TEXT,
            signature TEXT,
            weight REAL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS data_packages(
            id TEXT PRIMARY KEY,
            path TEXT,
            kind TEXT,
            active INTEGER DEFAULT 1,
            minzoom INTEGER,
            maxzoom INTEGER,
            note TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS spectral_pixels(
            lat REAL,
            lon REAL,
            b2 REAL,
            b4 REAL,
            b6 REAL,
            b7 REAL,
            aster_silica REAL,
            lineament_density REAL,
            shear_intersection REAL,
            elevation REAL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_spectral_lat_lon ON spectral_pixels(lat, lon)")
        self.conn.commit()

    def seed_reference_data(self):
        c = self.conn.cursor()
        analogs = [
            ("A1", 19.793522, 36.556198, "GPZ Hand-Pit Dark Regolith", "dark slope, hand pits, micro-lineaments", 0.92),
            ("A2", 19.834457, 36.478347, "GPZ Regolith Loader Expansion", "wadi dark hills, hand pits to loader", 0.88),
            ("A3", 20.492444, 36.348738, "Dark Knoll/Pediment Hand-Pit", "dark knoll near wadi", 0.84),
            ("A4", 20.494440, 36.360965, "Hybrid Wadi Corridor", "dark surface plus wadi corridor", 0.83),
            ("A5", 19.547212, 36.280184, "Dark Pediment/Hill-Foot Strip", "hill foot dark regolith and loader strips", 0.86),
            ("A6", 21.075710, 36.341820, "Mountain Feeder/Wadi Interface", "feeder gullies to main wadi", 0.82),
        ]
        c.executemany("INSERT OR IGNORE INTO analogs VALUES(?,?,?,?,?,?)", analogs)

        # KCL minimal seed. Replace/extend using CSV import when full Klemm table is ready.
        klemm = [
            ("KCL_TIBIRI", "Tibiri", 0.0, 0.0, "Klemm", "oxidized quartz cavities", "vein/shear", "hematite/limonite", "rich quartz cavity", 3),
            ("KCL_HADANAIB", "Hadanaib", 0.0, 0.0, "Klemm", "red quartz/limonite hematite", "vein", "iron oxide/red alteration", "red quartz better than white opaque", 3),
            ("KCL_RIGAG", "Rigag Sageib", 0.0, 0.0, "Klemm", "quartz cavities", "shear-hosted", "oxidation", "visible gold shear cavity", 3),
            ("KCL_KAMOLI", "Kamoli/Wadi Rak", 0.0, 0.0, "Klemm", "graphite schist boudinaged quartz", "deformation zone", "quartz/gabbro/granite", "Hamisana deformation analog", 3),
        ]
        c.executemany("INSERT OR IGNORE INTO klemm_sites VALUES(?,?,?,?,?,?,?,?,?,?)", klemm)

        candidates = [
            ("Z01", 20.802185, 36.380156, "ASTER/Landsat/Sentinel HOLD+", "fusion screening candidate", 0.79),
            ("Z02", 20.754163, 36.371198, "ASTER/Landsat/Sentinel HOLD+", "fusion screening candidate", 0.78),
            ("Z03", 20.904043, 36.449256, "ASTER/Landsat/Sentinel HOLD+", "fusion screening candidate", 0.76),
            ("Z04", 20.794075, 36.432736, "ASTER/Landsat/Sentinel HOLD+", "fusion screening candidate", 0.75),
            ("Z05", 20.727652, 36.422116, "ASTER/Landsat/Sentinel HOLD+", "fusion screening candidate", 0.75),
            ("TARGET_B", 20.780500, 36.450700, "Target B HOLD+", "SWIR brightness high; final needs raw/DEM/field", 0.70),
        ]
        c.executemany("INSERT OR IGNORE INTO analogs VALUES(?,?,?,?,?,?)", candidates)
        self.conn.commit()

    def nearest_klemm(self, lat: float, lon: float) -> Tuple[str, float, float]:
        best_name, best_d, best_b = "none", 999999.0, 0.0
        for r in self.conn.execute("SELECT * FROM klemm_sites WHERE lat != 0 AND lon != 0"):
            d = haversine_km(lat, lon, r["lat"], r["lon"])
            if d < best_d:
                best_d = d
                best_name = r["name"]
                best_b = bearing_deg(lat, lon, r["lat"], r["lon"])
        return best_name, best_d, best_b

    def nearest_analog(self, lat: float, lon: float) -> Tuple[str, str, float, float]:
        best_id, best_kind, best_d, best_w = "none", "none", 999999.0, 0.0
        for r in self.conn.execute("SELECT * FROM analogs"):
            d = haversine_km(lat, lon, r["lat"], r["lon"])
            if d < best_d:
                best_d = d
                best_id = r["id"]
                best_kind = r["kind"]
                best_w = r["weight"]
        return best_id, best_kind, best_d, best_w

    def query_spectral_pixel(self, lat: float, lon: float) -> SpectralPixel:
        # nearest neighbor from local SQLite sidecar table
        row = self.conn.execute("""
            SELECT *, ((lat-?)*(lat-?) + (lon-?)*(lon-?)) AS dd
            FROM spectral_pixels
            ORDER BY dd ASC
            LIMIT 1
        """, (lat, lat, lon, lon)).fetchone()
        if not row:
            return SpectralPixel()
        return SpectralPixel(
            b2=float(row["b2"] or 0), b4=float(row["b4"] or 0),
            b6=float(row["b6"] or 0), b7=float(row["b7"] or 0),
            silica=float(row["aster_silica"] or 0),
            lineament_density=float(row["lineament_density"] or 0),
            shear_intersection=float(row["shear_intersection"] or 0),
            elevation=float(row["elevation"] or 0),
            source="spectral_pixels_sqlite"
        )

    def save_target(self, payload: Dict[str, Any]):
        cols = ",".join(payload.keys())
        qs = ",".join(["?"] * len(payload))
        vals = list(payload.values())
        self.conn.execute(f"INSERT OR REPLACE INTO targets({cols}) VALUES({qs})", vals)
        self.conn.commit()

    def list_targets(self) -> List[sqlite3.Row]:
        return list(self.conn.execute("SELECT * FROM targets ORDER BY ts DESC LIMIT 200"))


class BouhEngine:
    def __init__(self, db: BouhDatabase):
        self.db = db

    def analyze(self, lat: float, lon: float, indicators: Dict[str, int], note: str = "") -> Dict[str, Any]:
        sp = self.db.query_spectral_pixel(lat, lon)
        clay = sp.b6 / sp.b7 if sp.b7 else 0.0
        iron = sp.b4 / sp.b2 if sp.b2 else 0.0
        silica = sp.silica
        lineament = sp.lineament_density
        elevation = sp.elevation

        nearest_klemm, d_klemm, b_klemm = self.db.nearest_klemm(lat, lon)
        analog_id, analog_kind, d_analog, analog_w = self.db.nearest_analog(lat, lon)

        # Strict numeric engine. Values from actual sidecar if present; otherwise zero.
        S = 0.0
        A = 0.0
        P = 0.0
        F = 0.0
        kill = 0
        reasons = []

        # Structure numeric score
        S += min(100.0, lineament * 100.0)
        if indicators.get("structure", 0): S += 45.0
        if indicators.get("shear", 0): S += 25.0
        if indicators.get("wadi", 0): P += 15.0
        if indicators.get("pattern", 0): P += 45.0
        if d_analog <= 3.0:
            P += 15.0
            F += 15.0 * analog_w
            reasons.append(f"analog_distance_km={d_analog:.3f}; analog_id={analog_id}")
        elif d_analog <= 8.0:
            F += 7.0 * analog_w
            reasons.append(f"regional_analog_distance_km={d_analog:.3f}; analog_id={analog_id}")

        # Alteration numeric score
        if clay > 0:
            A += min(40.0, clay * 20.0)
        if iron > 0:
            A += min(20.0, iron * 8.0)
        if silica > 0:
            A += min(30.0, silica * 30.0)
        if indicators.get("quartz", 0): A += 25.0
        if indicators.get("clay_red", 0): A += 20.0
        if indicators.get("dark_regolith", 0): F += 20.0
        if indicators.get("old_work", 0): F += 15.0
        if indicators.get("gpz_repeat", 0): F += 35.0
        if indicators.get("virgin", 0): P += 15.0

        # Klemm proximity
        if d_klemm < 2.0:
            F += 15.0
            reasons.append(f"klemm_distance_km={d_klemm:.3f}; klemm={nearest_klemm}; bearing={b_klemm:.2f}")
        elif d_klemm < 10.0:
            F += 6.0
            reasons.append(f"klemm_regional_distance_km={d_klemm:.3f}; klemm={nearest_klemm}; bearing={b_klemm:.2f}")

        S = min(100.0, S)
        A = min(100.0, A)
        P = min(100.0, P)
        F = min(100.0, F)

        confidence = (0.35 * S) + (0.30 * A) + (0.20 * P) + (0.15 * F)

        # Kill/Hold logic
        has_structure = (S >= 20.0) or indicators.get("structure", 0) or indicators.get("shear", 0)
        has_quartz_or_clay = (clay > 0 and clay >= 1.05) or (silica > 0) or indicators.get("quartz", 0) or indicators.get("clay_red", 0)
        has_field = indicators.get("gpz_repeat", 0) or indicators.get("old_work", 0)

        if not has_structure and not indicators.get("pattern", 0):
            if not has_field:
                kill = 1
                confidence = 0.0
                reasons.append("KILL=1; no_structure_and_no_pattern")
            else:
                confidence = min(confidence, 54.0)
                reasons.append("HOLD; field_evidence_without_clear_structure_pattern")

        if not has_quartz_or_clay and not indicators.get("dark_regolith", 0):
            confidence = min(confidence, 69.0)
            reasons.append("HOLD; no_clay_silica_quartz_dark")

        if confidence >= 85.0 and has_structure and has_quartz_or_clay:
            cls = "S-Tier Target"
            decision = "FIELD_PRIORITY_1"
        elif confidence >= 70.0:
            cls = "Candidate"
            decision = "FIELD_CHECK"
        elif confidence >= 55.0:
            cls = "HOLD"
            decision = "FAST_CHECK_ONLY"
        else:
            cls = "KILL" if kill else "LOW"
            decision = "DO_NOT_DIG"

        return {
            "id": f"BOUH_{now_ms()}",
            "ts": now_ms(),
            "lat": lat,
            "lon": lon,
            "score": round(confidence, 2),
            "cls": cls,
            "decision": decision,
            "clay": round(clay, 6),
            "iron": round(iron, 6),
            "silica": round(silica, 6),
            "lineament": round(lineament, 6),
            "elevation": round(elevation, 3),
            "distance_klemm_km": round(d_klemm, 3) if d_klemm < 999999 else 0.0,
            "nearest_klemm": nearest_klemm,
            "nearest_analog": analog_id,
            "nearest_analog_km": round(d_analog, 3),
            "bearing_klemm_deg": round(b_klemm, 2),
            "source": sp.source,
            "kill": kill,
            "reasons": "; ".join(reasons),
            "note": note
        }


class TileCanvas(FloatLayout):
    status = StringProperty("MBTiles inactive")
    zoom = NumericProperty(10)
    center_lat = NumericProperty(20.0)
    center_lon = NumericProperty(36.5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mbtiles_path = ""
        self.bind(pos=self.draw_grid, size=self.draw_grid)
        Clock.schedule_once(lambda dt: self.draw_grid(), 0.2)

    def draw_grid(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.02, 0.05, 0.02, 1)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.12, 0.25, 0.12, 1)
            for i in range(0, int(self.width), 64):
                Line(points=[self.x+i, self.y, self.x+i, self.y+self.height], width=1)
            for j in range(0, int(self.height), 64):
                Line(points=[self.x, self.y+j, self.x+self.width, self.y+j], width=1)
            Color(0.85, 0.72, 0.29, 1)
            Ellipse(pos=(self.center_x-6, self.center_y-6), size=(12, 12))
            Line(points=[self.center_x, self.y, self.center_x, self.y+self.height], width=1.2)
            Line(points=[self.x, self.center_y, self.x+self.width, self.center_y], width=1.2)


class LabeledCheck(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(36), **kwargs)
        self.checkbox = CheckBox(size_hint_x=None, width=dp(48))
        self.add_widget(self.checkbox)
        self.add_widget(Label(text=text, color=(0.88, 1, 0.88, 1), halign="right"))

    def active(self):
        return 1 if self.checkbox.active else 0


class BouhRoot(BoxLayout):
    def __init__(self, db: BouhDatabase, engine: BouhEngine, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.db = db
        self.engine = engine
        self.current_lat = 20.0
        self.current_lon = 36.5
        self.build_ui()

    def add_header(self):
        self.clear_widgets()
        self.add_widget(Label(
            text="BOUH TERRAIN | ABU AZIZA SYSTEM V5",
            size_hint_y=None, height=dp(38),
            color=(0.85, 0.72, 0.29, 1), bold=True
        ))
        nav = GridLayout(cols=4, size_hint_y=None, height=dp(92), spacing=dp(4), padding=dp(4))
        for text, fn in [
            ("Dashboard", self.show_dashboard),
            ("Map/3D", self.show_map),
            ("Analyze", self.show_analyze),
            ("Data", self.show_data),
            ("Klemm", self.show_klemm),
            ("Targets", self.show_targets),
            ("AI", self.show_ai),
            ("Security", self.show_security),
        ]:
            b = Button(text=text, background_color=(0.85, 0.72, 0.29, 1), color=(0.02, 0.05, 0.02, 1))
            b.bind(on_release=lambda _, f=fn: f())
            nav.add_widget(b)
        self.add_widget(nav)

    def content(self):
        sv = ScrollView()
        box = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(8), spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        sv.add_widget(box)
        self.add_widget(sv)
        return box

    def card_label(self, box, title, body):
        box.add_widget(Label(text=f"[b]{title}[/b]\n{body}", markup=True, color=(0.9, 1, 0.9, 1),
                             size_hint_y=None, text_size=(None, None), halign="right", valign="top",
                             height=dp(220)))

    def build_ui(self):
        self.show_dashboard()

    def show_dashboard(self):
        self.add_header()
        box = self.content()
        targets = self.db.list_targets()
        body = (
            f"developer={DEVELOPER}\n"
            f"mode=Python Native/Kivy; npm=0; expo=0\n"
            f"data_dir={DATA_DIR}\n"
            f"targets_count={len(targets)}\n"
            f"strict_numeric=enabled\n"
            f"terrain_rgb_equation=Elevation=-10000+((R*256*256+G*256+B)*0.1)\n"
            f"target_score_range=0.00_to_100.00\n"
            f"kill_rule=no_structure_and_no_pattern=>0.00 unless field evidence\n"
            f"raw_bands_status=external_sidecar_required\n"
        )
        self.card_label(box, "SYSTEM STATUS", body)

    def show_map(self):
        self.add_header()
        layout = BoxLayout(orientation="vertical")
        tc = TileCanvas(size_hint_y=0.72)
        layout.add_widget(tc)
        info = Label(
            text=f"center_lat={self.current_lat:.6f}; center_lon={self.current_lon:.6f}; zoom={tc.zoom}; mbtiles_path={os.path.join(DATA_DIR,'mbtiles')}",
            size_hint_y=0.12, color=(0.9, 1, 0.9, 1)
        )
        layout.add_widget(info)
        row = GridLayout(cols=3, size_hint_y=0.16)
        for text, fn in [("GPS", self.start_gps), ("Analyze Center", self.show_analyze), ("Open Google Maps", self.open_maps)]:
            b = Button(text=text, background_color=(0.85,0.72,0.29,1), color=(0.02,0.05,0.02,1))
            b.bind(on_release=lambda _, f=fn: f())
            row.add_widget(b)
        layout.add_widget(row)
        self.add_widget(layout)

    def show_analyze(self):
        self.add_header()
        box = self.content()

        latlon = GridLayout(cols=2, size_hint_y=None, height=dp(96))
        self.lat_in = TextInput(text=fnum(self.current_lat), multiline=False, input_filter="float")
        self.lon_in = TextInput(text=fnum(self.current_lon), multiline=False, input_filter="float")
        latlon.add_widget(self.lat_in)
        latlon.add_widget(self.lon_in)
        box.add_widget(latlon)

        self.note_in = TextInput(hint_text="numeric field note / GPZ / quartz / dark regolith", size_hint_y=None, height=dp(92))
        box.add_widget(self.note_in)

        checks = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        checks.bind(minimum_height=checks.setter("height"))
        self.chk = {}
        for key, text in [
            ("structure", "structure=1"),
            ("shear", "shear_zone=1"),
            ("pattern", "pattern_cluster=1"),
            ("quartz", "quartz_silica=1"),
            ("clay_red", "clay_red_alteration=1"),
            ("dark_regolith", "dark_regolith=1"),
            ("wadi", "wadi_edge_feeder=1"),
            ("old_work", "old_work_loader_analog=1"),
            ("gpz_repeat", "gpz_repeat_signal=1"),
            ("virgin", "virgin_pre_digging_similarity=1"),
        ]:
            lc = LabeledCheck(text)
            self.chk[key] = lc
            checks.add_widget(lc)
        box.add_widget(checks)

        run = Button(text="RUN NUMERIC TARGET ANALYSIS", size_hint_y=None, height=dp(52),
                     background_color=(0.85, 0.72, 0.29, 1), color=(0.02,0.05,0.02,1))
        run.bind(on_release=lambda _: self.run_analysis())
        box.add_widget(run)

        self.result = Label(text="result=none", color=(0.9,1,0.9,1), halign="right", size_hint_y=None, height=dp(320))
        box.add_widget(self.result)

    def run_analysis(self):
        lat = float(self.lat_in.text or 0)
        lon = float(self.lon_in.text or 0)
        indicators = {k: v.active() for k, v in self.chk.items()}
        out = self.engine.analyze(lat, lon, indicators, self.note_in.text)
        save_payload = {k: out[k] for k in [
            "id", "ts", "lat", "lon", "score", "cls", "decision", "clay", "iron", "silica",
            "lineament", "elevation", "distance_klemm_km", "nearest_klemm", "reasons", "note"
        ]}
        self.db.save_target(save_payload)
        if out["score"] > 85.0:
            self.enqueue_mail(out)
        self.result.text = "\n".join([f"{k}={v}" for k, v in out.items()])

    def show_data(self):
        self.add_header()
        box = self.content()
        body = (
            "required_packages:\n"
            "1) mbtiles/base/*.mbtiles zoom=5..18\n"
            "2) terrain_rgb/*.mbtiles png_tiles terrain-rgb\n"
            "3) spectral/spectral_pixels.sqlite table=spectral_pixels\n"
            "4) klemm/klemm_sites.sqlite or CSV import\n\n"
            "storage_path_android=/Android/data/com.abuaziza.bouhgoldpro/files/BOUH_DATA/\n"
            f"runtime_path={DATA_DIR}\n"
            "import_status=manual_file_copy_usb_c\n"
        )
        self.card_label(box, "DATA PACKAGE MANAGER", body)

    def show_klemm(self):
        self.add_header()
        box = self.content()
        rows = self.db.conn.execute("SELECT * FROM klemm_sites ORDER BY reliability DESC, name ASC").fetchall()
        text = "id,name,lat,lon,lithology,structure,alteration,analog_class,reliability\n"
        for r in rows:
            text += f"{r['id']},{r['name']},{r['lat']},{r['lon']},{r['lithology']},{r['structure']},{r['alteration']},{r['analog_class']},{r['reliability']}\n"
        self.card_label(box, "KLEMM CLUSTER ENGINE", text)

    def show_targets(self):
        self.add_header()
        box = self.content()
        rows = self.db.list_targets()
        text = "id,lat,lon,score,cls,decision,clay,iron,silica,lineament,elevation,nearest_klemm\n"
        for r in rows:
            text += f"{r['id']},{r['lat']:.6f},{r['lon']:.6f},{r['score']:.2f},{r['cls']},{r['decision']},{r['clay']:.6f},{r['iron']:.6f},{r['silica']:.6f},{r['lineament']:.6f},{r['elevation']:.2f},{r['nearest_klemm']}\n"
        btn = Button(text="COPY CSV", size_hint_y=None, height=dp(48))
        btn.bind(on_release=lambda _: Clipboard.copy(text))
        box.add_widget(btn)
        self.card_label(box, "TARGET REGISTER", text)

    def show_ai(self):
        self.add_header()
        box = self.content()
        self.ai_in = TextInput(hint_text="numeric/plain field description: quartz=1 dark=1 wadi=1 gpz=1", size_hint_y=None, height=dp(120))
        box.add_widget(self.ai_in)
        b = Button(text="RUN OFFLINE RULE INFERENCE", size_hint_y=None, height=dp(48))
        b.bind(on_release=lambda _: self.ai_rule())
        box.add_widget(b)
        self.ai_out = Label(text="ai_output=none", size_hint_y=None, height=dp(320), color=(0.9,1,0.9,1))
        box.add_widget(self.ai_out)

    def ai_rule(self):
        s = self.ai_in.text.lower()
        score = 0
        vals = {
            "quartz": 1 if "quartz" in s or "كوارتز" in s else 0,
            "dark": 1 if "dark" in s or "سود" in s or "داكن" in s else 0,
            "wadi": 1 if "wadi" in s or "وادي" in s or "شعب" in s else 0,
            "gpz": 1 if "gpz" in s or "اشارة" in s or "إشارة" in s else 0,
            "oldwork": 1 if "loader" in s or "لودر" in s or "حفر" in s else 0,
            "structure": 1 if "structure" in s or "كسر" in s or "بنية" in s else 0,
        }
        score = (25*vals["structure"] + 20*vals["quartz"] + 15*vals["dark"] + 15*vals["wadi"] + 15*vals["gpz"] + 10*vals["oldwork"])
        if vals["structure"] == 0 and vals["gpz"] == 0:
            score = 0
        self.ai_out.text = f"rule_score={score:.2f}%\n" + "\n".join([f"{k}={v}" for k,v in vals.items()])

    def show_security(self):
        self.add_header()
        box = self.content()
        self.pass_in = TextInput(password=True, hint_text="engineer password", size_hint_y=None, height=dp(48))
        box.add_widget(self.pass_in)
        b = Button(text="SAVE LOCAL PASSWORD HASH", size_hint_y=None, height=dp(48))
        b.bind(on_release=lambda _: self.save_security_hash())
        box.add_widget(b)
        self.card_label(box, "SECURITY", "sqlcipher_status=planned_if_python_package_available\npbkdf2=enabled\nsecret_not_hardcoded=1\nsmtp_password_not_hardcoded=1\nsilent_sync=queue_only_until_endpoint_configured")

    def save_security_hash(self):
        ensure_dirs()
        salt = os.urandom(16)
        key = pbkdf2_key(self.pass_in.text, salt)
        cfg = self.load_config()
        cfg["password_salt_hex"] = salt.hex()
        cfg["password_hash_hex"] = hashlib.sha256(key).hexdigest()
        self.save_config(cfg)
        self.popup("security_saved=1")

    def start_gps(self):
        if gps is None:
            self.popup("gps_provider=unavailable_in_this_runtime")
            return
        try:
            gps.configure(on_location=self.on_location, on_status=lambda stype, status: None)
            gps.start(minTime=1000, minDistance=1)
            self.popup("gps_started=1")
        except Exception as e:
            self.popup(f"gps_error={e}")

    def on_location(self, **kwargs):
        self.current_lat = float(kwargs.get("lat", self.current_lat))
        self.current_lon = float(kwargs.get("lon", self.current_lon))

    def open_maps(self):
        uri = f"https://www.google.com/maps/search/?api=1&query={self.current_lat:.6f},{self.current_lon:.6f}"
        try:
            import webbrowser
            webbrowser.open(uri)
        except Exception:
            Clipboard.copy(uri)
            self.popup("maps_url_copied=1")

    def enqueue_mail(self, payload: Dict[str, Any]):
        ensure_dirs()
        cfg = self.load_config()
        password = cfg.get("local_queue_password", "BOUH_LOCAL_QUEUE")
        encrypted = pseudo_encrypt_text(json.dumps(payload, ensure_ascii=False), password)
        with open(QUEUE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": now_ms(), "to": TARGET_EMAIL, "encrypted": encrypted}, ensure_ascii=False) + "\n")

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            return {}
        try:
            return json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
        except Exception:
            return {}

    def save_config(self, cfg):
        json.dump(cfg, open(CONFIG_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    def popup(self, msg):
        Popup(title="BOUH", content=Label(text=msg), size_hint=(0.88, 0.32)).open()


class BouhV5App(App):
    def build(self):
        ensure_dirs()
        db = BouhDatabase()
        engine = BouhEngine(db)
        return BouhRoot(db, engine)


if __name__ == "__main__":
    BouhV5App().run()

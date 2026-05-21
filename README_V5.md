# BOUH Terrain | Abu Aziza System V5

## Folder Structure

```text
BOUH_TERRAIN_V5/
├── app.py
├── requirements.txt
├── buildozer.spec
├── .github/
│   └── workflows/
│       └── ONE_CLICK_BUILD_APK.yml
└── BOUH_DATA/
    ├── mbtiles/
    │   ├── base_map_zoom_5_18.mbtiles
    │   └── terrain_rgb_zoom_5_18.mbtiles
    ├── spectral/
    │   └── spectral_pixels.sqlite
    ├── klemm/
    │   └── klemm_sites.sqlite or klemm_sites.csv
    ├── imports/
    │   ├── targets.csv
    │   ├── analogs.csv
    │   └── studies.csv
    └── mail_queue.jsonl
```

## Android field data path

```text
/Android/data/com.abuaziza.bouhgoldpro/files/BOUH_DATA/
```

## SQLite table required for pixel-level analysis

```sql
CREATE TABLE spectral_pixels(
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
);
CREATE INDEX idx_spectral_lat_lon ON spectral_pixels(lat, lon);
```

## Terrain-RGB formula

```text
Elevation = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)
```

## Truth boundary

This V5 app can calculate real numeric spectral indices only when `spectral_pixels.sqlite` or equivalent local raw sidecar data exists.
Without that file, spectral numeric values are zero and the app explicitly reports `source=no_raw_pixel`.

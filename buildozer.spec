[app]

# ------------------------------------------------------------
# BOUH Terrain | Abu Aziza System V5
# Python Native / Kivy / No npm / No Expo
# ------------------------------------------------------------

title = BOUH GOLD V12.5

package.name = bouhgold
package.domain = com.abuaziza

source.dir = .
source.include_exts = py,kv,json,txt,sqlite,db,mbtiles,csv,kml,kmz,gpx,png,jpg,jpeg

version = 12.5.5

# ------------------------------------------------------------
# Requirements
# ------------------------------------------------------------
# ملاحظة:
# sqlite3 و hashlib و json و math و os مكتبات Python داخلية.
# لا تضف sqlite3 هنا.
# plyer يستخدم GPS / sensors عند توفرها.
# ------------------------------------------------------------

requirements = python3,kivy==2.3.0,plyer==2.1.0

# ------------------------------------------------------------
# Android settings
# ------------------------------------------------------------

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 35
android.minapi = 23
android.ndk = 25b

android.archs = arm64-v8a,armeabi-v7a

android.allow_backup = True
android.private_storage = True

# ------------------------------------------------------------
# Build system
# ------------------------------------------------------------

p4a.branch = master

# ------------------------------------------------------------
# App resources
# ------------------------------------------------------------

# icon.filename =
# presplash.filename =

# ------------------------------------------------------------
# Storage / data packages
# ------------------------------------------------------------
# ضع ملفات البيانات الكبيرة لاحقاً داخل الهاتف في:
# /Android/data/com.abuaziza.bouhgoldpro/files/BOUH_DATA/
#
# أمثلة:
# BOUH_DATA/mbtiles/base_map_zoom_5_18.mbtiles
# BOUH_DATA/mbtiles/terrain_rgb_zoom_5_18.mbtiles
# BOUH_DATA/spectral/spectral_pixels.sqlite
# BOUH_DATA/klemm/klemm_sites.sqlite
# ------------------------------------------------------------

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

log_level = 2
warn_on_root = 0


[buildozer]

log_level = 2
warn_on_root = 0

import sys
import os
import json

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Create default data files if missing
PROFILES_PATH = os.path.join(DATA_DIR, "profiles.json")
PRESETS_PATH  = os.path.join(DATA_DIR, "presets.json")

DEFAULT_PROFILES = {
    "profiles": [
        {
            "id": "default",
            "name": "Default User",
            "color": "#00b4d8",
            "active_preset": "media",
            "created_at": "2024-01-01"
        }
    ],
    "active_profile": "default",
    "save_path": DATA_DIR
}

DEFAULT_PRESETS = {
    "media": {
        "label": "Media Player",
        "icon": "M",
        "color": "#00b4d8",
        "mappings": {
            "OPEN_PALM":   {"type": "media_key", "key": "media_play_pause", "label": "Play / Pause"},
            "FIST":        {"type": "media_key", "key": "media_volume_mute","label": "Mute"},
            "SWIPE_RIGHT": {"type": "media_key", "key": "media_next",       "label": "Next Track"},
            "SWIPE_LEFT":  {"type": "media_key", "key": "media_previous",   "label": "Prev Track"},
            "THUMBS_UP":   {"type": "media_key", "key": "media_volume_up",  "label": "Volume Up"},
            "THUMBS_DOWN": {"type": "media_key", "key": "media_volume_down","label": "Volume Down"},
            "PEACE":       {"type": "hotkey",    "keys": ["ctrl","l"],      "label": "Focus Search"}
        }
    },
    "browser": {
        "label": "Browser",
        "icon": "B",
        "color": "#a855f7",
        "mappings": {
            "SWIPE_LEFT":  {"type": "hotkey", "keys": ["alt","left"],  "label": "Go Back"},
            "SWIPE_RIGHT": {"type": "hotkey", "keys": ["alt","right"], "label": "Go Forward"},
            "SWIPE_UP":    {"type": "scroll", "dx": 0, "dy": 5,        "label": "Scroll Up"},
            "SWIPE_DOWN":  {"type": "scroll", "dx": 0, "dy": -5,       "label": "Scroll Down"},
            "OPEN_PALM":   {"type": "hotkey", "keys": ["ctrl","t"],    "label": "New Tab"},
            "FIST":        {"type": "hotkey", "keys": ["ctrl","w"],    "label": "Close Tab"},
            "PEACE":       {"type": "hotkey", "keys": ["ctrl","r"],    "label": "Refresh"},
            "THUMBS_UP":   {"type": "key",    "key": "page_up",        "label": "Page Up"},
            "THUMBS_DOWN": {"type": "key",    "key": "page_down",      "label": "Page Down"}
        }
    },
    "gaming": {
        "label": "Gaming",
        "icon": "G",
        "color": "#f72585",
        "mappings": {
            "OPEN_PALM":   {"type": "key", "key": "space", "label": "Jump"},
            "FIST":        {"type": "key", "key": "e",     "label": "Interact"},
            "SWIPE_LEFT":  {"type": "key", "key": "a",     "label": "Move Left"},
            "SWIPE_RIGHT": {"type": "key", "key": "d",     "label": "Move Right"},
            "SWIPE_UP":    {"type": "key", "key": "w",     "label": "Move Forward"},
            "SWIPE_DOWN":  {"type": "key", "key": "s",     "label": "Move Back"},
            "THUMBS_UP":   {"type": "key", "key": "r",     "label": "Reload"},
            "THUMBS_DOWN": {"type": "key", "key": "c",     "label": "Crouch"},
            "PEACE":       {"type": "key", "key": "tab",   "label": "Scoreboard"},
            "POINT":       {"type": "key", "key": "f",     "label": "Use / Fire"}
        }
    },
    "navigation": {
        "label": "Navigation",
        "icon": "N",
        "color": "#06d6a0",
        "mappings": {
            "SWIPE_LEFT":  {"type": "hotkey", "keys": ["alt","left"],   "label": "Back"},
            "SWIPE_RIGHT": {"type": "hotkey", "keys": ["alt","right"],  "label": "Forward"},
            "SWIPE_UP":    {"type": "scroll", "dx": 0, "dy": 3,         "label": "Scroll Up"},
            "SWIPE_DOWN":  {"type": "scroll", "dx": 0, "dy": -3,        "label": "Scroll Down"},
            "OPEN_PALM":   {"type": "hotkey", "keys": ["ctrl","home"],  "label": "Go to Top"},
            "FIST":        {"type": "hotkey", "keys": ["ctrl","end"],   "label": "Go to Bottom"},
            "THUMBS_UP":   {"type": "key",    "key": "page_up",         "label": "Page Up"},
            "THUMBS_DOWN": {"type": "key",    "key": "page_down",       "label": "Page Down"}
        }
    }
}

if not os.path.exists(PROFILES_PATH):
    with open(PROFILES_PATH, "w") as f:
        json.dump(DEFAULT_PROFILES, f, indent=2)

if not os.path.exists(PRESETS_PATH):
    with open(PRESETS_PATH, "w") as f:
        json.dump(DEFAULT_PRESETS, f, indent=2)

# ── Launch app ────────────────────────────────────────────────────────────────
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QLockFile, Qt
from app.main_window import MainWindow
from app.styles import STYLE

def _acquire_lock():
    global APP_LOCK
    lock_path = os.path.join(DATA_DIR, "gestureflow.lock")
    APP_LOCK = QLockFile(lock_path)
    APP_LOCK.setStaleLockTime(1000)
    if not APP_LOCK.tryLock(100):
        APP_LOCK.removeStaleLockFile()
        if not APP_LOCK.tryLock(100):
            try:
                os.remove(lock_path)
                APP_LOCK = QLockFile(lock_path)
                return APP_LOCK.tryLock(100)
            except Exception:
                return False
    return True

def main():
    if not _acquire_lock():
        print("GestureFlow is already running.")
        return

    app = QApplication(sys.argv)
    app.setApplicationName("GestureFlow")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow(BASE_DIR)
    window.show()
    app.aboutToQuit.connect(APP_LOCK.unlock)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

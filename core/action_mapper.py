import json
import os
import math
import ctypes
import time

try:
    from pynput.keyboard import Key, Controller as KbController
    from pynput.mouse    import Button, Controller as MouseController
    _pynput_ok = True
except Exception:
    _pynput_ok = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from comtypes import CLSCTX_ALL
    _audio_ok = True
except Exception:
    _audio_ok = False

_KEY_MAP = {
    # Media
    "media_play_pause":  "media_play_pause",
    "media_volume_up":   "media_volume_up",
    "media_volume_down": "media_volume_down",
    "media_volume_mute": "media_volume_mute",
    "media_next":        "media_next",
    "media_previous":    "media_previous",
    # Navigation
    "page_up":    "page_up",
    "page_down":  "page_down",
    "home":       "home",
    "end":        "end",
    # Modifiers
    "ctrl":  "ctrl",
    "alt":   "alt",
    "shift": "shift",
    "cmd":   "cmd",
    # Misc
    "space": "space",
    "tab":   "tab",
    "esc":   "esc",
    "enter": "enter",
    "backspace": "backspace",
    "delete": "delete",
    "left":  "left",
    "right": "right",
    "up":    "up",
    "down":  "down",
    "f5": "f5",
}


def _resolve_key(name: str):
    """Return a pynput Key or a plain char string."""
    if not _pynput_ok:
        return None
    name = name.lower()
    if name in _KEY_MAP:
        attr = _KEY_MAP[name]
        return getattr(Key, attr, name)
    return name   # single char like 'a','w','r' etc.


class ActionMapper:
    def __init__(self, presets_path: str, cursor_alpha: float = 0.25,
                 cursor_deadzone: int = 6, profiles_path: str = None):
        self.presets_path   = presets_path
        self.presets        = self._load()
        self.active_preset  = "media"
        self.profiles_path = profiles_path
        self.application_profiles = self._load_application_profiles()

        if _pynput_ok:
            self._kb    = KbController()
            self._mouse = MouseController()
        else:
            self._kb    = None
            self._mouse = None

        self.cursor_alpha = min(1.0, max(0.01, float(cursor_alpha)))
        self.cursor_deadzone = max(0, int(cursor_deadzone))
        self._smooth_cursor = None
        self._last_cursor = None
        self._dragging = False
        self.cursor_bounds = (0.05, 0.05, 0.95, 0.95)
        self._volume = None
        self._last_action_at = {}
        self.action_cooldown = 0.3
        if _audio_ok:
            try:
                device = AudioUtilities.GetSpeakers()
                interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._volume = interface.QueryInterface(IAudioEndpointVolume)
            except Exception:
                self._volume = None

    # ── I/O ───────────────────────────────────────────────────────────────────
    def _load(self):
        try:
            with open(self.presets_path) as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_application_profiles(self):
        if not self.profiles_path:
            return {}
        try:
            with open(self.profiles_path) as profiles_file:
                return json.load(profiles_file).get("application_profiles", {})
        except (OSError, ValueError):
            return {}

    def refresh_application_profile(self):
        if os.name != "nt" or not self.application_profiles:
            return
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            handle = ctypes.windll.kernel32.OpenProcess(0x0410, False, pid.value)
            buffer = ctypes.create_unicode_buffer(260)
            ctypes.windll.psapi.GetModuleBaseNameW(handle, None, buffer, 260)
            ctypes.windll.kernel32.CloseHandle(handle)
            preset = self.application_profiles.get(buffer.value.lower())
            if preset in self.presets and preset != self.active_preset:
                self.active_preset = preset
        except Exception:
            return

    def set_application_profile(self, executable: str, preset_id: str):
        executable = executable.strip().lower()
        if executable and preset_id in self.presets:
            self.application_profiles[executable] = preset_id
            self._save_application_profiles()

    def _save_application_profiles(self):
        if not self.profiles_path:
            return
        try:
            with open(self.profiles_path) as profiles_file:
                data = json.load(profiles_file)
            data["application_profiles"] = self.application_profiles
            with open(self.profiles_path, "w") as profiles_file:
                json.dump(data, profiles_file, indent=2)
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(self.presets_path, "w") as f:
                json.dump(self.presets, f, indent=2)
        except Exception:
            pass

    # ── Public ────────────────────────────────────────────────────────────────
    def set_preset(self, preset_id: str):
        self.active_preset = preset_id

    def get_action_label(self, gesture: str) -> str:
        """Return human-readable label for current preset + gesture."""
        preset = self.presets.get(self.active_preset, {})
        mappings = preset.get("mappings", {})
        action = mappings.get(gesture, {})
        return action.get("label", "")

    def execute(self, gesture: str):
        """Fire the action mapped to this gesture in the active preset."""
        if not _pynput_ok or not self._kb:
            return
        preset   = self.presets.get(self.active_preset, {})
        mappings = preset.get("mappings", {})
        action   = mappings.get(gesture)
        if not action:
            return
        now = time.monotonic()
        if now - self._last_action_at.get(gesture, 0.0) < self.action_cooldown:
            return
        try:
            self._perform(action)
            self._last_action_at[gesture] = now
        except Exception:
            pass

    def update_cursor(self, x: float, y: float, screen_width: int,
                      screen_height: int):
        if not self._mouse:
            return
        left, top, right, bottom = self.cursor_bounds
        dx = right - left if right > left else 1.0
        dy = bottom - top if bottom > top else 1.0
        mapped_x = (float(x) - left) / dx
        mapped_y = (float(y) - top) / dy
        target = (
            max(0, min(screen_width - 1, int(mapped_x * screen_width))),
            max(0, min(screen_height - 1, int(mapped_y * screen_height))),
        )
        if self._smooth_cursor is None:
            self._smooth_cursor = target
            self._last_cursor = target
            self._mouse.position = target
            return
        self._smooth_cursor = (
            self.cursor_alpha * target[0] + (1 - self.cursor_alpha) * self._smooth_cursor[0],
            self.cursor_alpha * target[1] + (1 - self.cursor_alpha) * self._smooth_cursor[1],
        )
        candidate = (round(self._smooth_cursor[0]), round(self._smooth_cursor[1]))
        if math.hypot(candidate[0] - self._last_cursor[0],
                      candidate[1] - self._last_cursor[1]) >= self.cursor_deadzone:
            self._mouse.position = candidate
            self._last_cursor = candidate

    def reset_cursor(self):
        self._smooth_cursor = None
        self._last_cursor = None

    def set_dragging(self, dragging: bool):
        if not self._mouse or dragging == self._dragging:
            return
        try:
            if dragging:
                self._mouse.press(Button.left)
            else:
                self._mouse.release(Button.left)
            self._dragging = dragging
        except Exception:
            self._dragging = False

    def release_drag(self):
        self.set_dragging(False)

    def set_cursor_alpha(self, alpha: float):
        self.cursor_alpha = min(1.0, max(0.01, float(alpha)))

    def set_cursor_bounds(self, left: float, top: float,
                          right: float, bottom: float):
        self.cursor_bounds = (
            min(0.49, max(0.0, float(left))),
            min(0.49, max(0.0, float(top))),
            max(0.51, min(1.0, float(right))),
            max(0.51, min(1.0, float(bottom))),
        )

    def update_volume(self, pinch_distance: float, active: bool):
        if not self._volume:
            return
        if not active:
            return
        volume = (float(pinch_distance) - 0.05) / 0.37
        self._volume.SetMasterVolumeLevelScalar(max(0.0, min(1.0, volume)), None)

    def _perform(self, action: dict):
        atype = action.get("type")

        if atype == "media_key":
            key = _resolve_key(action["key"])
            if key:
                self._kb.press(key)
                self._kb.release(key)

        elif atype == "hotkey":
            keys = [_resolve_key(k) for k in action.get("keys", [])]
            keys = [k for k in keys if k]
            for k in keys:
                self._kb.press(k)
            for k in reversed(keys):
                self._kb.release(k)

        elif atype == "key":
            key = _resolve_key(action["key"])
            if key:
                self._kb.press(key)
                self._kb.release(key)

        elif atype == "scroll":
            if self._mouse:
                self._mouse.scroll(action.get("dx", 0), action.get("dy", 0))

        elif atype == "click":
            if self._mouse:
                self._mouse.click(Button.left)

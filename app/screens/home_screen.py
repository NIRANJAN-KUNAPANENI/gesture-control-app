import json
import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout,
    QDialog, QLineEdit, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui  import QColor


PRESET_ORDER = ["media", "browser", "gaming", "navigation"]

PRESET_DESCRIPTIONS = {
    "media":      "Control media playback with gestures.\nPlay, Pause, Skip, Volume.",
    "browser":    "Navigate your browser hands-free.\nScroll, Tab, Back, Forward.",
    "gaming":     "Full game control via gestures.\nMove, Jump, Interact, Reload.",
    "navigation": "System-level navigation.\nScroll, Page, Home, End.",
}


class ProfileDialog(QDialog):
    def __init__(self, parent=None, existing_name=""):
        super().__init__(parent)
        self.setWindowTitle("Profile")
        self.setFixedSize(360, 160)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        lbl = QLabel("PROFILE NAME")
        lbl.setObjectName("h3")
        layout.addWidget(lbl)

        self.name_input = QLineEdit(existing_name)
        self.name_input.setPlaceholderText("Enter profile name...")
        layout.addWidget(self.name_input)

        btn_row = QHBoxLayout()
        cancel = QPushButton("CANCEL")
        cancel.setObjectName("ghost_btn")
        cancel.clicked.connect(self.reject)

        save = QPushButton("SAVE")
        save.setObjectName("primary_btn")
        save.clicked.connect(self.accept)

        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)


class HomeScreen(QWidget):
    COLORS = ["#00b4d8", "#a855f7", "#f72585", "#06d6a0", "#f59e0b"]

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.profiles_path = main_window.profiles_path
        self.presets_path  = main_window.presets_path
        self.profiles_data = self._load_profiles()
        self.presets_data  = self._load_presets()

        self._build_ui()
        self.refresh_ui()

    def _load_profiles(self):
        try:
            with open(self.profiles_path) as f:
                return json.load(f)
        except Exception:
            return {"profiles": [], "active_profile": None, "save_path": ""}

    def _load_presets(self):
        try:
            with open(self.presets_path) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_profiles(self):
        with open(self.profiles_path, "w") as f:
            json.dump(self.profiles_data, f, indent=2)

    # ── UI Build ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(0)

        left = QVBoxLayout()
        left.setSpacing(4)
        self.welcome_label = QLabel("WELCOME BACK")
        self.welcome_label.setObjectName("h1")
        self.time_label = QLabel("")
        self.time_label.setObjectName("muted")

        left.addWidget(self.welcome_label)
        left.addWidget(self.time_label)
        hdr.addLayout(left)
        hdr.addStretch()

        launch_btn = QPushButton("LAUNCH CONTROL  →")
        launch_btn.setObjectName("primary_btn")
        launch_btn.setCursor(Qt.PointingHandCursor)
        launch_btn.clicked.connect(lambda: self.main_window.navigate_to(1))
        hdr.addWidget(launch_btn)

        root.addLayout(hdr)
        root.addSpacing(32)

        # ── Profiles section ──────────────────────────────────────────────────
        lbl_row = QHBoxLayout()
        profiles_lbl = QLabel("PROFILES")
        profiles_lbl.setObjectName("h3")
        lbl_row.addWidget(profiles_lbl)
        lbl_row.addStretch()

        add_btn = QPushButton("+ NEW PROFILE")
        add_btn.setObjectName("ghost_btn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_profile)
        lbl_row.addWidget(add_btn)
        root.addLayout(lbl_row)
        root.addSpacing(14)

        # Profile cards scroll area
        self.profiles_container = QWidget()
        self.profiles_layout    = QHBoxLayout(self.profiles_container)
        self.profiles_layout.setContentsMargins(0, 0, 0, 0)
        self.profiles_layout.setSpacing(14)
        self.profiles_layout.addStretch()

        profiles_scroll = QScrollArea()
        profiles_scroll.setWidget(self.profiles_container)
        profiles_scroll.setWidgetResizable(True)
        profiles_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        profiles_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        profiles_scroll.setFixedHeight(130)
        profiles_scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(profiles_scroll)

        root.addSpacing(32)

        # ── Presets section ───────────────────────────────────────────────────
        presets_lbl = QLabel("CONTROL PRESETS")
        presets_lbl.setObjectName("h3")
        root.addWidget(presets_lbl)
        root.addSpacing(14)

        self.presets_grid = QGridLayout()
        self.presets_grid.setSpacing(14)
        root.addLayout(self.presets_grid)

        root.addStretch()

        # Clock timer
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._update_time)
        self._clock.start(1000)
        self._update_time()

    def _update_time(self):
        now = datetime.now()
        self.time_label.setText(
            now.strftime("%A, %d %B %Y  ·  %H:%M:%S").upper()
        )

    # ── Refresh ───────────────────────────────────────────────────────────────
    def refresh_ui(self):
        self.profiles_data = self._load_profiles()
        self._render_profiles()
        self._render_presets()
        self._update_welcome()

    def _update_welcome(self):
        active_id = self.profiles_data.get("active_profile")
        profiles  = self.profiles_data.get("profiles", [])
        name = "USER"
        for p in profiles:
            if p["id"] == active_id:
                name = p["name"].upper()
                break
        self.welcome_label.setText(f"WELCOME BACK, {name}")

    def _render_profiles(self):
        # Clear existing
        for i in reversed(range(self.profiles_layout.count())):
            item = self.profiles_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        profiles  = self.profiles_data.get("profiles", [])
        active_id = self.profiles_data.get("active_profile")

        for idx, profile in enumerate(profiles):
            card = self._make_profile_card(profile, active_id, idx)
            self.profiles_layout.insertWidget(idx, card)

    def _make_profile_card(self, profile, active_id, idx):
        is_active = profile["id"] == active_id
        color     = profile.get("color", self.COLORS[idx % len(self.COLORS)])
        initial   = profile["name"][0].upper()

        card = QFrame()
        card.setObjectName("card_accent" if is_active else "card")
        card.setFixedSize(180, 100)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        top = QHBoxLayout()
        avatar = QLabel(initial)
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(
            f"background:{color}; color:#080b14; font-weight:900; "
            f"font-size:16px; border-radius:18px;"
        )
        top.addWidget(avatar)
        top.addStretch()
        if is_active:
            dot = QLabel("ACTIVE")
            dot.setObjectName("badge_success")
            top.addWidget(dot)

        name_lbl = QLabel(profile["name"])
        name_lbl.setStyleSheet("font-weight:700; font-size:13px; color:#e2e8f0;")

        preset_lbl = QLabel(profile.get("active_preset", "media").upper())
        preset_lbl.setStyleSheet("font-size:10px; color:#334155; letter-spacing:2px;")

        layout.addLayout(top)
        layout.addWidget(name_lbl)
        layout.addWidget(preset_lbl)

        # Click → activate
        card.mousePressEvent = lambda e, pid=profile["id"]: self._activate_profile(pid)

        # Context: right-click → delete
        card.setContextMenuPolicy(Qt.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, pid=profile["id"], pname=profile["name"]:
                self._delete_profile(pid, pname)
        )

        return card

    def _render_presets(self):
        # Clear
        for i in reversed(range(self.presets_grid.count())):
            item = self.presets_grid.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        active_id    = self.profiles_data.get("active_profile")
        profiles     = self.profiles_data.get("profiles", [])
        active_preset = "media"
        for p in profiles:
            if p["id"] == active_id:
                active_preset = p.get("active_preset", "media")
                break

        for col, pid in enumerate(PRESET_ORDER):
            data = self.presets_data.get(pid, {})
            if not data:
                continue
            card = self._make_preset_card(pid, data, pid == active_preset)
            self.presets_grid.addWidget(card, 0, col)

    def _make_preset_card(self, pid, data, is_active):
        color  = data.get("color", "#00b4d8")
        label  = data.get("label", pid.upper())
        icon   = data.get("icon", pid[0].upper())
        desc   = PRESET_DESCRIPTIONS.get(pid, "")
        mappings = data.get("mappings", {})
        n_gestures = len(mappings)

        card = QFrame()
        card.setObjectName("card_accent" if is_active else "card_glow")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(200)
        card.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Icon circle
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"background:{'#061624' if is_active else '#0a0e1a'}; "
            f"color:{color}; font-weight:900; font-size:20px; border-radius:24px; "
            f"border:{'1px solid ' + color if is_active else '1px solid #0f1929'};"
        )

        name_lbl = QLabel(label.upper())
        name_lbl.setStyleSheet(
            f"font-weight:900; font-size:15px; "
            f"color:{'#00b4d8' if is_active else '#94a3b8'}; letter-spacing:2px;"
        )

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color:#334155; font-size:11px; line-height:160%;")
        desc_lbl.setWordWrap(True)

        gestures_lbl = QLabel(f"{n_gestures} GESTURES MAPPED")
        gestures_lbl.setStyleSheet(
            f"color:{color if is_active else '#1e3a5f'}; "
            f"font-size:10px; font-weight:700; letter-spacing:2px;"
        )

        if is_active:
            badge = QLabel("ACTIVE")
            badge.setObjectName("badge_success")
        else:
            badge = QPushButton("SET ACTIVE")
            badge.setObjectName("ghost_btn")
            badge.setCursor(Qt.PointingHandCursor)
            badge.clicked.connect(lambda _, p=pid: self._set_preset(p))

        layout.addWidget(icon_lbl)
        layout.addWidget(name_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()
        layout.addWidget(gestures_lbl)
        layout.addWidget(badge)

        if not is_active:
            card.mousePressEvent = lambda e, p=pid: self._set_preset(p)

        return card

    # ── Actions ───────────────────────────────────────────────────────────────
    def _activate_profile(self, pid: str):
        self.profiles_data["active_profile"] = pid
        self._save_profiles()
        self.refresh_ui()

    def _add_profile(self):
        dlg = ProfileDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            name = dlg.name_input.text().strip()
            if not name:
                return
            import uuid
            new_id = str(uuid.uuid4())[:8]
            color  = self.COLORS[len(self.profiles_data["profiles"]) % len(self.COLORS)]
            self.profiles_data["profiles"].append({
                "id": new_id, "name": name, "color": color,
                "active_preset": "media",
                "created_at": datetime.now().strftime("%Y-%m-%d")
            })
            self.profiles_data["active_profile"] = new_id
            self._save_profiles()
            self.refresh_ui()

    def _delete_profile(self, pid: str, name: str):
        if len(self.profiles_data["profiles"]) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "At least one profile is required.")
            return
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Delete profile '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.profiles_data["profiles"] = [
                p for p in self.profiles_data["profiles"] if p["id"] != pid
            ]
            if self.profiles_data["active_profile"] == pid:
                self.profiles_data["active_profile"] = self.profiles_data["profiles"][0]["id"]
            self._save_profiles()
            self.refresh_ui()

    def _set_preset(self, preset_id: str):
        active_id = self.profiles_data.get("active_profile")
        for p in self.profiles_data["profiles"]:
            if p["id"] == active_id:
                p["active_preset"] = preset_id
                break
        self._save_profiles()
        self.main_window.action_mapper.set_preset(preset_id)
        self.refresh_ui()

    def on_activated(self):
        self.refresh_ui()

import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QLineEdit, QSpinBox,
    QSlider, QScrollArea, QFileDialog, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt


GESTURE_CHEATSHEET = [
    ("Open Palm",   "All 5 fingers extended",    "#00b4d8"),
    ("Fist",        "All fingers closed",         "#ef4444"),
    ("Thumbs Up",   "Only thumb up",              "#06d6a0"),
    ("Thumbs Down", "Thumb pointing down",        "#f59e0b"),
    ("Peace / V",   "Index + middle extended",    "#a855f7"),
    ("Point",       "Only index finger",          "#f72585"),
    ("Pinch",       "Thumb + index together",     "#f59e0b"),
    ("OK Sign",     "Thumb + index tips touch",   "#06d6a0"),
    ("Rock / Horns","Index + pinky extended",     "#f72585"),
    ("Call Me",     "Thumb + pinky extended",     "#a855f7"),
    ("Three",       "Index + middle + ring",      "#00b4d8"),
    ("Four",        "Four fingers extended",      "#00b4d8"),
    ("Swipe Left",  "Move hand left quickly",     "#00b4d8"),
    ("Swipe Right", "Move hand right quickly",    "#00b4d8"),
    ("Swipe Up",    "Move hand upward quickly",   "#00b4d8"),
    ("Swipe Down",  "Move hand downward quickly", "#00b4d8"),
]


class SettingsScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window   = main_window
        self.profiles_path = main_window.profiles_path
        self.profiles_data = self._load_profiles()
        self.presets_path = main_window.presets_path
        self.presets_data = self._load_presets()

        self._build_ui()
        self._load_current_settings()

    def _load_profiles(self):
        try:
            with open(self.profiles_path) as f:
                return json.load(f)
        except Exception:
            return {"save_path": ""}

    def _save_profiles(self):
        with open(self.profiles_path, "w") as f:
            json.dump(self.profiles_data, f, indent=2)

    def _load_presets(self):
        try:
            with open(self.presets_path) as presets_file:
                return json.load(presets_file)
        except (OSError, ValueError):
            return {}

    def _save_presets(self):
        with open(self.presets_path, "w") as presets_file:
            json.dump(self.presets_data, presets_file, indent=2)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(40, 32, 40, 40)
        layout.setSpacing(32)

        # ── Page header ───────────────────────────────────────────────────────
        hdr = QLabel("SYSTEM SETTINGS")
        hdr.setObjectName("h1")
        layout.addWidget(hdr)

        sub = QLabel("Configure camera, detection, and data storage preferences.")
        sub.setObjectName("muted")
        layout.addWidget(sub)

        layout.addWidget(self._divider())

        # ── Camera settings ───────────────────────────────────────────────────
        layout.addWidget(self._section_label("CAMERA CONFIGURATION"))

        cam_card = QFrame()
        cam_card.setObjectName("card")
        cam_layout = QVBoxLayout(cam_card)
        cam_layout.setContentsMargins(24, 24, 24, 24)
        cam_layout.setSpacing(18)

        # Camera index
        cam_idx_row = QHBoxLayout()
        lbl = QLabel("Camera Index")
        lbl.setStyleSheet("font-size:13px; color:#94a3b8;")
        hint = QLabel("0 = built-in webcam, 1+ = external")
        hint.setObjectName("muted")

        lbl_col = QVBoxLayout()
        lbl_col.addWidget(lbl)
        lbl_col.addWidget(hint)

        self.cam_idx_spin = QSpinBox()
        self.cam_idx_spin.setMinimum(0)
        self.cam_idx_spin.setMaximum(10)
        self.cam_idx_spin.setFixedWidth(90)

        cam_idx_row.addLayout(lbl_col)
        cam_idx_row.addStretch()
        cam_idx_row.addWidget(self.cam_idx_spin)
        cam_layout.addLayout(cam_idx_row)

        # Mirror toggle
        mirror_row = QHBoxLayout()
        mirror_lbl_col = QVBoxLayout()
        mirror_lbl_col.addWidget(self._setting_label("Mirror Feed"))
        mirror_lbl_col.addWidget(self._hint_label("Flip camera horizontally (recommended)"))
        self.mirror_check = QCheckBox()
        self.mirror_check.setChecked(True)
        mirror_row.addLayout(mirror_lbl_col)
        mirror_row.addStretch()
        mirror_row.addWidget(self.mirror_check)
        cam_layout.addLayout(mirror_row)

        layout.addWidget(cam_card)

        # ── Detection settings ────────────────────────────────────────────────
        layout.addWidget(self._section_label("DETECTION PARAMETERS"))

        det_card = QFrame()
        det_card.setObjectName("card")
        det_layout = QVBoxLayout(det_card)
        det_layout.setContentsMargins(24, 24, 24, 24)
        det_layout.setSpacing(20)

        # Confidence
        conf_col = QVBoxLayout()
        conf_hdr = QHBoxLayout()
        conf_hdr.addWidget(self._setting_label("Detection Confidence"))
        self.conf_val_lbl = QLabel("70%")
        self.conf_val_lbl.setObjectName("accent")
        conf_hdr.addStretch()
        conf_hdr.addWidget(self.conf_val_lbl)
        conf_col.addLayout(conf_hdr)
        conf_col.addWidget(self._hint_label(
            "Higher = more accurate but slower. Recommended: 60–80%"
        ))
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(30, 95)
        self.conf_slider.setValue(70)
        self.conf_slider.valueChanged.connect(
            lambda v: self.conf_val_lbl.setText(f"{v}%")
        )
        conf_col.addWidget(self.conf_slider)
        det_layout.addLayout(conf_col)

        det_layout.addWidget(self._divider())

        # Gesture cooldown
        cool_col = QVBoxLayout()
        cool_hdr = QHBoxLayout()
        cool_hdr.addWidget(self._setting_label("Gesture Cooldown"))
        self.cool_val_lbl = QLabel("0.9s")
        self.cool_val_lbl.setObjectName("accent")
        cool_hdr.addStretch()
        cool_hdr.addWidget(self.cool_val_lbl)
        cool_col.addLayout(cool_hdr)
        cool_col.addWidget(self._hint_label(
            "Minimum time between gesture actions. Lower = faster, Higher = less noise."
        ))
        self.cool_slider = QSlider(Qt.Horizontal)
        self.cool_slider.setRange(3, 30)   # 0.3s to 3.0s (×0.1)
        self.cool_slider.setValue(9)
        self.cool_slider.valueChanged.connect(
            lambda v: self.cool_val_lbl.setText(f"{v/10:.1f}s")
        )
        cool_col.addWidget(self.cool_slider)
        det_layout.addLayout(cool_col)

        layout.addWidget(det_card)

        layout.addWidget(self._section_label("ACTION SAFETY"))
        safety_card = QFrame()
        safety_card.setObjectName("card")
        safety_layout = QVBoxLayout(safety_card)
        safety_layout.setContentsMargins(24, 20, 24, 20)
        safety_layout.setSpacing(10)
        safety_row = QHBoxLayout()
        safety_row.addWidget(self._setting_label("Minimum action confidence"))
        self.action_conf_value = QLabel("65%")
        self.action_conf_value.setObjectName("accent")
        safety_row.addStretch()
        safety_row.addWidget(self.action_conf_value)
        safety_layout.addLayout(safety_row)
        safety_layout.addWidget(self._hint_label("Actions are ignored below this confidence."))
        self.action_conf_slider = QSlider(Qt.Horizontal)
        self.action_conf_slider.setRange(50, 95)
        self.action_conf_slider.setValue(65)
        self.action_conf_slider.valueChanged.connect(
            lambda value: self.action_conf_value.setText(f"{value}%")
        )
        safety_layout.addWidget(self.action_conf_slider)
        layout.addWidget(safety_card)

        # ── Data storage ──────────────────────────────────────────────────────
        layout.addWidget(self._section_label("DATA STORAGE"))

        data_card = QFrame()
        data_card.setObjectName("card")
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(24, 24, 24, 24)
        data_layout.setSpacing(14)

        data_layout.addWidget(self._setting_label("Save Path"))
        data_layout.addWidget(self._hint_label(
            "Location where profiles, presets, and recordings are stored."
        ))

        path_row = QHBoxLayout()
        self.save_path_input = QLineEdit()
        self.save_path_input.setPlaceholderText("Select a folder...")
        browse_btn = QPushButton("BROWSE")
        browse_btn.setObjectName("ghost_btn")
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_path)
        browse_btn.setFixedWidth(100)
        path_row.addWidget(self.save_path_input)
        path_row.addWidget(browse_btn)
        data_layout.addLayout(path_row)

        layout.addWidget(data_card)

        # ── Gesture cheatsheet ────────────────────────────────────────────────
        layout.addWidget(self._section_label("GESTURE REFERENCE"))

        cheat_card = QFrame()
        cheat_card.setObjectName("card")
        cheat_layout = QVBoxLayout(cheat_card)
        cheat_layout.setContentsMargins(24, 20, 24, 20)
        cheat_layout.setSpacing(10)

        for gesture, description, color in GESTURE_CHEATSHEET:
            row = QHBoxLayout()
            row.setSpacing(16)

            g_lbl = QLabel(gesture.upper())
            g_lbl.setFixedWidth(140)
            g_lbl.setStyleSheet(
                f"color:{color}; font-weight:700; font-size:11px; letter-spacing:2px;"
            )

            d_lbl = QLabel(description)
            d_lbl.setStyleSheet("color:#475569; font-size:12px;")

            row.addWidget(g_lbl)
            row.addWidget(d_lbl)
            row.addStretch()
            cheat_layout.addLayout(row)

        layout.addWidget(cheat_card)

        layout.addWidget(self._section_label("GESTURE ACTION EDITOR"))
        editor_card = QFrame()
        editor_card.setObjectName("card")
        editor_layout = QVBoxLayout(editor_card)
        editor_layout.setContentsMargins(24, 20, 24, 20)
        editor_layout.setSpacing(10)

        self.editor_preset = QComboBox()
        self.editor_gesture = QComboBox()
        self.editor_type = QComboBox()
        self.editor_type.addItems(["key", "media_key", "hotkey", "scroll", "click"])
        self.editor_value = QLineEdit()
        self.editor_value.setPlaceholderText("Key, media key, or comma-separated hotkeys")
        for preset_id, preset in self.presets_data.items():
            self.editor_preset.addItem(preset.get("label", preset_id.title()), preset_id)
        self.editor_preset.currentIndexChanged.connect(self._refresh_editor_gestures)
        self.editor_gesture.currentIndexChanged.connect(self._load_editor_action)
        editor_layout.addWidget(self._setting_label("Preset"))
        editor_layout.addWidget(self.editor_preset)
        editor_layout.addWidget(self._setting_label("Gesture"))
        editor_layout.addWidget(self.editor_gesture)
        editor_layout.addWidget(self._setting_label("Action type"))
        editor_layout.addWidget(self.editor_type)
        editor_layout.addWidget(self._setting_label("Action value"))
        editor_layout.addWidget(self.editor_value)
        save_action = QPushButton("SAVE GESTURE ACTION")
        save_action.setObjectName("primary_btn")
        save_action.clicked.connect(self._save_editor_action)
        editor_layout.addWidget(save_action)
        layout.addWidget(editor_card)
        self._refresh_editor_gestures()

        layout.addWidget(self._section_label("APPLICATION PROFILES"))
        app_card = QFrame()
        app_card.setObjectName("card")
        app_layout = QVBoxLayout(app_card)
        app_layout.setContentsMargins(24, 20, 24, 20)
        app_layout.setSpacing(10)
        app_hint = self._hint_label("Example: chrome.exe uses the Browser preset.")
        self.app_executable = QLineEdit()
        self.app_executable.setPlaceholderText("Application executable, e.g. chrome.exe")
        self.app_preset = QComboBox()
        for preset_id, preset in self.presets_data.items():
            self.app_preset.addItem(preset.get("label", preset_id.title()), preset_id)
        app_save = QPushButton("SAVE APPLICATION PROFILE")
        app_save.setObjectName("secondary_btn")
        app_save.clicked.connect(self._save_application_profile)
        app_layout.addWidget(app_hint)
        app_layout.addWidget(self.app_executable)
        app_layout.addWidget(self.app_preset)
        app_layout.addWidget(app_save)
        layout.addWidget(app_card)

        # ── About ─────────────────────────────────────────────────────────────
        layout.addWidget(self._section_label("ABOUT"))

        about_card = QFrame()
        about_card.setObjectName("card")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(24, 20, 24, 20)
        about_layout.setSpacing(8)

        for key, val in [
            ("Application",  "GestureFlow"),
            ("Version",      "1.0.0"),
            ("Framework",    "PyQt5 + MediaPipe + OpenCV"),
            ("ML Engine",    "MediaPipe Hands (CNN landmark detection)"),
            ("Action Layer", "pynput keyboard/mouse/media controller"),
        ]:
            row = QHBoxLayout()
            k_lbl = QLabel(key.upper())
            k_lbl.setFixedWidth(140)
            k_lbl.setObjectName("muted")
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet("color:#64748b; font-size:12px;")
            row.addWidget(k_lbl)
            row.addWidget(v_lbl)
            row.addStretch()
            about_layout.addLayout(row)

        layout.addWidget(about_card)

        # ── Save button ───────────────────────────────────────────────────────
        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_btn = QPushButton("SAVE SETTINGS")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_settings)
        save_row.addWidget(self.save_btn)
        layout.addLayout(save_row)

        layout.addSpacing(20)

        scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("h3")
        return lbl

    def _setting_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-size:13px; color:#94a3b8; font-weight:600;")
        return lbl

    def _hint_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("muted")
        lbl.setWordWrap(True)
        return lbl

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    # ── Load / Save ───────────────────────────────────────────────────────────
    def _load_current_settings(self):
        self.save_path_input.setText(
            self.profiles_data.get("save_path", self.main_window.data_dir)
        )
        self.cam_idx_spin.setValue(
            self.profiles_data.get("camera_index", 0)
        )
        conf = int(self.profiles_data.get("detection_confidence", 0.7) * 100)
        self.conf_slider.setValue(conf)
        cool = int(self.profiles_data.get("gesture_cooldown", 0.9) * 10)
        self.cool_slider.setValue(cool)
        action_confidence = int(self.profiles_data.get("action_confidence", 0.65) * 100)
        self.action_conf_slider.setValue(action_confidence)
        self.main_window.cam_thread.set_camera_index(self.cam_idx_spin.value())
        self.main_window.cam_thread.set_confidence(conf)
        self.main_window.cam_thread.action_confidence = action_confidence / 100.0

    def _browse_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self.save_path_input.setText(folder)

    def _refresh_editor_gestures(self):
        self.editor_gesture.blockSignals(True)
        self.editor_gesture.clear()
        preset = self.presets_data.get(self.editor_preset.currentData(), {})
        for gesture in preset.get("mappings", {}):
            self.editor_gesture.addItem(gesture)
        self.editor_gesture.blockSignals(False)
        self._load_editor_action()

    def _load_editor_action(self):
        preset = self.presets_data.get(self.editor_preset.currentData(), {})
        action = preset.get("mappings", {}).get(self.editor_gesture.currentText(), {})
        self.editor_type.setCurrentText(action.get("type", "key"))
        if action.get("type") == "hotkey":
            self.editor_value.setText(",".join(action.get("keys", [])))
        else:
            self.editor_value.setText(action.get("key", ""))

    def _save_editor_action(self):
        preset = self.presets_data.get(self.editor_preset.currentData(), {})
        gesture = self.editor_gesture.currentText()
        action_type = self.editor_type.currentText()
        value = self.editor_value.text().strip()
        if not gesture or not value:
            return
        action = {"type": action_type, "label": f"{action_type}: {value}"}
        if action_type == "hotkey":
            action["keys"] = [key.strip() for key in value.split(",") if key.strip()]
        elif action_type == "click":
            action["label"] = "Mouse click"
        else:
            action["key"] = value
        preset.setdefault("mappings", {})[gesture] = action
        self._save_presets()
        self.main_window.action_mapper.presets = self.presets_data

    def _save_application_profile(self):
        self.main_window.action_mapper.set_application_profile(
            self.app_executable.text(), self.app_preset.currentData()
        )
        self.app_executable.clear()

    def _save_settings(self):
        cam_idx  = self.cam_idx_spin.value()
        conf     = self.conf_slider.value() / 100.0
        cooldown = self.cool_slider.value() / 10.0
        action_confidence = self.action_conf_slider.value() / 100.0
        path     = self.save_path_input.text().strip()

        self.profiles_data["camera_index"]          = cam_idx
        self.profiles_data["detection_confidence"]  = conf
        self.profiles_data["gesture_cooldown"]      = cooldown
        self.profiles_data["action_confidence"]     = action_confidence
        self.profiles_data["save_path"]             = path
        self._save_profiles()

        # Apply to engine
        self.main_window.cam_thread.set_camera_index(cam_idx)
        self.main_window.cam_thread.set_confidence(conf)
        if self.main_window.cam_thread.engine:
            self.main_window.cam_thread.engine.set_cooldown(cooldown)
            self.main_window.cam_thread.engine.set_min_action_confidence(action_confidence)

        self.save_btn.setText("✓  SAVED")
        self.save_btn.setObjectName("success_btn")
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self._reset_save_btn)

    def _reset_save_btn(self):
        self.save_btn.setText("SAVE SETTINGS")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.style().unpolish(self.save_btn)
        self.save_btn.style().polish(self.save_btn)

    def on_activated(self):
        self._load_current_settings()

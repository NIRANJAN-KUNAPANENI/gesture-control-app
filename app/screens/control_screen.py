from datetime import datetime
import json

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSlider, QVBoxLayout, QWidget,
)

from core.camera_thread import CameraThread
from core.gesture_engine import GESTURE_META


class ControlScreen(QWidget):
    """Primary workspace for safe, visible gesture control."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cam_thread = main_window.cam_thread
        self.presets_data = self._load_presets()
        self._active = False
        self._frame_count = 0

        self._build_ui()
        self._load_preferences()
        self.cam_thread.frame_signal.connect(self._on_frame)
        self.cam_thread.gesture_signal.connect(self._on_gesture)
        self.cam_thread.calibration_complete.connect(self._on_calibration_complete)

        self._fps_timer = QTimer(self)
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(1000)

    def _load_presets(self):
        try:
            with open(self.main_window.presets_path) as presets_file:
                return json.load(presets_file)
        except (OSError, ValueError):
            return {}

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(18)

        header = QHBoxLayout()
        title_column = QVBoxLayout()
        title = QLabel("CONTROL")
        title.setObjectName("page_title")
        subtitle = QLabel("Use your hand as a quiet, precise remote.")
        subtitle.setObjectName("page_subtitle")
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        header.addLayout(title_column)
        header.addStretch()

        self.status_badge = QLabel("PAUSED")
        self.status_badge.setObjectName("status_badge_off")
        header.addWidget(self.status_badge, alignment=Qt.AlignTop)
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(18)

        camera_panel = QFrame()
        camera_panel.setObjectName("workspace_panel")
        camera_layout = QVBoxLayout(camera_panel)
        camera_layout.setContentsMargins(16, 16, 16, 16)
        camera_layout.setSpacing(12)

        self.cam_label = QLabel("CAMERA PAUSED")
        self.cam_label.setObjectName("camera_view")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setMinimumSize(620, 420)
        self.cam_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        camera_layout.addWidget(self.cam_label, 1)

        camera_footer = QHBoxLayout()
        self.fps_label = QLabel("-- FPS")
        self.hand_label = QLabel("NO HAND DETECTED")
        self.hand_label.setObjectName("muted_label")
        camera_footer.addWidget(self.fps_label)
        camera_footer.addStretch()
        camera_footer.addWidget(self.hand_label)
        camera_layout.addLayout(camera_footer)
        content.addWidget(camera_panel, 3)

        side = QVBoxLayout()
        side.setSpacing(12)

        gesture_panel = QFrame()
        gesture_panel.setObjectName("workspace_panel")
        gesture_layout = QVBoxLayout(gesture_panel)
        gesture_layout.setContentsMargins(20, 18, 20, 18)
        gesture_layout.setSpacing(6)

        overline = QLabel("NOW DETECTING")
        overline.setObjectName("panel_overline")
        self.gesture_label = QLabel("READY")
        self.gesture_label.setObjectName("gesture_value")
        self.action_label = QLabel("Start control to begin")
        self.action_label.setObjectName("muted_label")
        self.action_label.setWordWrap(True)
        gesture_layout.addWidget(overline)
        gesture_layout.addWidget(self.gesture_label)
        gesture_layout.addWidget(self.action_label)
        side.addWidget(gesture_panel)

        control_panel = QFrame()
        control_panel.setObjectName("workspace_panel")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(20, 18, 20, 18)
        control_layout.setSpacing(12)

        preset_title = QLabel("PROFILE")
        preset_title.setObjectName("panel_overline")
        self.preset_combo = QComboBox()
        for preset_id, preset in self.presets_data.items():
            self.preset_combo.addItem(preset.get("label", preset_id.title()), preset_id)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        control_layout.addWidget(preset_title)
        control_layout.addWidget(self.preset_combo)

        self.cursor_check = QCheckBox("Cursor control")
        self.cursor_check.setChecked(True)
        self.cursor_check.toggled.connect(self._set_cursor_enabled)
        self.volume_check = QCheckBox("Pinch volume")
        self.volume_check.setChecked(True)
        self.volume_check.toggled.connect(self._set_volume_enabled)
        self.click_check = QCheckBox("Pinch click / drag")
        self.click_check.setChecked(False)
        self.click_check.toggled.connect(self._set_click_enabled)
        control_layout.addWidget(self.cursor_check)
        control_layout.addWidget(self.volume_check)
        control_layout.addWidget(self.click_check)

        sensitivity_row = QHBoxLayout()
        sensitivity_label = QLabel("Cursor sensitivity")
        sensitivity_label.setObjectName("muted_label")
        self.sensitivity_value = QLabel("25%")
        self.sensitivity_value.setObjectName("muted_label")
        sensitivity_row.addWidget(sensitivity_label)
        sensitivity_row.addStretch()
        sensitivity_row.addWidget(self.sensitivity_value)
        control_layout.addLayout(sensitivity_row)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(10, 50)
        self.sensitivity_slider.setValue(25)
        self.sensitivity_slider.valueChanged.connect(self._set_sensitivity)
        control_layout.addWidget(self.sensitivity_slider)

        margin_row = QHBoxLayout()
        margin_label = QLabel("Edge margin")
        margin_label.setObjectName("muted_label")
        self.margin_value = QLabel("5%")
        self.margin_value.setObjectName("muted_label")
        margin_row.addWidget(margin_label)
        margin_row.addStretch()
        margin_row.addWidget(self.margin_value)
        control_layout.addLayout(margin_row)
        self.margin_slider = QSlider(Qt.Horizontal)
        self.margin_slider.setRange(0, 20)
        self.margin_slider.setValue(5)
        self.margin_slider.valueChanged.connect(self._set_margin)
        control_layout.addWidget(self.margin_slider)

        self.toggle_btn = QPushButton("START CONTROL")
        self.toggle_btn.setObjectName("primary_btn")
        self.toggle_btn.clicked.connect(self._toggle_control)
        control_layout.addWidget(self.toggle_btn)

        self.calibrate_btn = QPushButton("CALIBRATE CURSOR AREA")
        self.calibrate_btn.setObjectName("secondary_btn")
        self.calibrate_btn.clicked.connect(self._start_calibration)
        control_layout.addWidget(self.calibrate_btn)
        side.addWidget(control_panel)

        log_panel = QFrame()
        log_panel.setObjectName("workspace_panel")
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(20, 16, 20, 16)
        log_layout.setSpacing(8)
        log_header = QHBoxLayout()
        log_title = QLabel("RECENT ACTIONS")
        log_title.setObjectName("panel_overline")
        clear_btn = QPushButton("CLEAR")
        clear_btn.setObjectName("text_btn")
        clear_btn.clicked.connect(self._clear_log)
        log_header.addWidget(log_title)
        log_header.addStretch()
        log_header.addWidget(clear_btn)
        self.log_list = QListWidget()
        self.log_list.setMinimumHeight(118)
        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_list)
        side.addWidget(log_panel, 1)

        diagnostics_panel = QFrame()
        diagnostics_panel.setObjectName("workspace_panel")
        diagnostics_layout = QVBoxLayout(diagnostics_panel)
        diagnostics_layout.setContentsMargins(20, 14, 20, 14)
        diagnostics_layout.setSpacing(4)
        diagnostics_title = QLabel("SYSTEM STATUS")
        diagnostics_title.setObjectName("panel_overline")
        self.diagnostics_label = QLabel("Camera: starting\nModel: loading\nFPS: --")
        self.diagnostics_label.setObjectName("muted_label")
        copy_diagnostics = QPushButton("COPY DIAGNOSTICS")
        copy_diagnostics.setObjectName("text_btn")
        copy_diagnostics.clicked.connect(self._copy_diagnostics)
        diagnostics_layout.addWidget(diagnostics_title)
        diagnostics_layout.addWidget(self.diagnostics_label)
        diagnostics_layout.addWidget(copy_diagnostics)
        side.addWidget(diagnostics_panel)

        content.addLayout(side, 1)
        root.addLayout(content, 1)

    def _on_frame(self, image):
        self._frame_count += 1
        if self._active:
            self.cam_label.setPixmap(QPixmap.fromImage(image).scaled(
                self.cam_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

    def _on_gesture(self, displayed, triggered, confidence=0.0, processing_ms=0.0):
        engine = self.cam_thread.engine
        model_status = "Loaded" if engine and engine.interpreter else "Rules fallback"
        camera_status = "Connected" if self.cam_thread.isRunning() else "Stopped"
        self._diagnostics_text = (
            f"Camera: {camera_status}\n"
            f"Model: {model_status}\n"
            f"Confidence: {confidence:.0%}\n"
            f"Processing: {processing_ms:.0f} ms\n"
            f"FPS: {self.fps_label.text()}"
        )
        self.diagnostics_label.setText(self._diagnostics_text)
        if not self._active:
            return
        if displayed in ("NONE", "UNKNOWN", ""):
            self.gesture_label.setText("READY")
            self.gesture_label.setStyleSheet("")
            message = ("Show an open palm to unlock"
                       if not self.cam_thread.control_unlocked
                       else "Show a supported gesture")
            self.action_label.setText(f"{message}  |  {processing_ms:.0f} ms")
            self.hand_label.setText("NO HAND DETECTED")
            return

        meta = GESTURE_META.get(displayed, GESTURE_META["UNKNOWN"])
        self.gesture_label.setText(meta["desc"].upper())
        self.gesture_label.setStyleSheet(f"color: {meta['color']};")
        action = self.main_window.action_mapper.get_action_label(displayed)
        if displayed == "OPEN_PALM" and self.cam_thread.control_unlocked:
            self.action_label.setText("CONTROL UNLOCKED")
        else:
            self.action_label.setText(
                f"{action or 'No action assigned'}  |  Confidence {confidence:.0%}"
            )
        self.hand_label.setText("HAND DETECTED")

        if triggered:
            item = QListWidgetItem(
                f"{datetime.now().strftime('%H:%M:%S')}   {meta['desc']}   {action or 'No action'}"
            )
            item.setForeground(QColor(meta["color"]))
            self.log_list.insertItem(0, item)
            while self.log_list.count() > 8:
                self.log_list.takeItem(self.log_list.count() - 1)

    def _update_fps(self):
        self.fps_label.setText(f"{self._frame_count} FPS")
        self._frame_count = 0

    def _toggle_control(self):
        self._active = not self._active
        if self._active:
            self.cam_thread.set_mode(CameraThread.MODE_CONTROL)
            self.cam_thread.set_control_enabled(True)
            self.toggle_btn.setText("STOP CONTROL")
            self.toggle_btn.setObjectName("danger_btn")
            self.status_badge.setText("LIVE")
            self.status_badge.setObjectName("status_badge_on")
            self.cam_label.setText("")
        else:
            self.cam_thread.set_mode(CameraThread.MODE_IDLE)
            self.cam_thread.set_control_enabled(False)
            self.toggle_btn.setText("START CONTROL")
            self.toggle_btn.setObjectName("primary_btn")
            self.status_badge.setText("PAUSED")
            self.status_badge.setObjectName("status_badge_off")
            self.cam_label.clear()
            self.cam_label.setText("CAMERA PAUSED")
            self.gesture_label.setText("READY")
            self.action_label.setText("Start control to begin")
        for widget in (self.toggle_btn, self.status_badge):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _on_preset_changed(self, index):
        preset_id = self.preset_combo.itemData(index)
        if preset_id:
            self.main_window.action_mapper.set_preset(preset_id)

    def _reset_cursor(self):
        self.main_window.action_mapper.reset_cursor()
        self.action_label.setText("Cursor position reset")

    def _start_calibration(self):
        if not self._active:
            self.action_label.setText("Start control before calibrating")
            return
        self.main_window.action_mapper.reset_cursor()
        self.cam_thread.start_calibration()
        self.action_label.setText("Move your index finger around the usable area")

    def _on_calibration_complete(self, left, top, right, bottom):
        self.main_window.action_mapper.set_cursor_bounds(left, top, right, bottom)
        self._save_preferences(cursor_bounds=[left, top, right, bottom])
        self.action_label.setText("Cursor area calibrated")

    def _load_preferences(self):
        try:
            with open(self.main_window.profiles_path) as profiles_file:
                preferences = json.load(profiles_file)
        except (OSError, ValueError):
            preferences = {}
        self.cursor_check.setChecked(preferences.get("cursor_enabled", True))
        self.volume_check.setChecked(preferences.get("volume_enabled", True))
        self.click_check.setChecked(preferences.get("click_enabled", False))
        alpha = int(float(preferences.get("cursor_alpha", 0.25)) * 100)
        margin = int(float(preferences.get("cursor_margin", 0.05)) * 100)
        self.sensitivity_slider.setValue(max(10, min(50, alpha)))
        self.margin_slider.setValue(max(0, min(20, margin)))
        bounds = preferences.get("cursor_bounds")
        if isinstance(bounds, list) and len(bounds) == 4:
            self.main_window.action_mapper.set_cursor_bounds(*bounds)

    def _save_preferences(self, **values):
        try:
            with open(self.main_window.profiles_path) as profiles_file:
                preferences = json.load(profiles_file)
            preferences.update(values)
            with open(self.main_window.profiles_path, "w") as profiles_file:
                json.dump(preferences, profiles_file, indent=2)
        except (OSError, ValueError):
            pass

    def _set_sensitivity(self, value):
        self.sensitivity_value.setText(f"{value}%")
        self.main_window.action_mapper.set_cursor_alpha(value / 100.0)
        self._save_preferences(cursor_alpha=value / 100.0)

    def _set_cursor_enabled(self, enabled):
        self.cam_thread.set_cursor_enabled(enabled)
        self._save_preferences(cursor_enabled=bool(enabled))

    def _set_volume_enabled(self, enabled):
        self.cam_thread.set_volume_enabled(enabled)
        self._save_preferences(volume_enabled=bool(enabled))

    def _set_click_enabled(self, enabled):
        self.cam_thread.set_click_enabled(enabled)
        self._save_preferences(click_enabled=bool(enabled))

    def _set_margin(self, value):
        margin = value / 100.0
        self.margin_value.setText(f"{value}%")
        self.main_window.action_mapper.set_cursor_bounds(
            margin, margin, 1.0 - margin, 1.0 - margin
        )
        self._save_preferences(cursor_margin=margin)

    def _clear_log(self):
        self.log_list.clear()

    def _copy_diagnostics(self):
        QApplication.clipboard().setText(getattr(self, "_diagnostics_text", "No diagnostics yet"))
        self.action_label.setText("Diagnostics copied")

    def on_activated(self):
        pass
import json
import os
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QListWidget, QListWidgetItem,
    QLineEdit, QRadioButton, QButtonGroup, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui  import QPixmap, QColor

from core.camera_thread  import CameraThread
from core.gesture_engine import GESTURE_META


class RecorderScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window   = main_window
        self.cam_thread    = main_window.cam_thread
        self.save_path     = main_window.data_dir
        self.recordings_path = os.path.join(self.save_path, "recordings.json")
        self.recordings    = self._load_recordings()

        self._recording    = False
        self._record_data  = []
        self._current_detected = "NONE"

        self._build_ui()
        self._connect_signals()
        self._refresh_list()

    def _load_recordings(self):
        try:
            with open(self.recordings_path) as f:
                return json.load(f)
        except Exception:
            return []

    def _save_recordings(self):
        try:
            with open(self.recordings_path, "w") as f:
                json.dump(self.recordings, f, indent=2)
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ═══ LEFT: Camera feed ═══════════════════════════════════════════════
        left = QWidget()
        left.setStyleSheet("background:#050709;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(30, 28, 20, 28)
        left_layout.setSpacing(14)

        cam_title = QLabel("GESTURE RECORDER")
        cam_title.setObjectName("h3")
        left_layout.addWidget(cam_title)

        # Status
        self.rec_status = QLabel("STANDBY — POSITION YOUR HAND")
        self.rec_status.setStyleSheet(
            "color:#334155; font-size:12px; font-weight:600; letter-spacing:2px;"
        )
        left_layout.addWidget(self.rec_status)

        # Camera
        self.cam_frame = QFrame()
        self.cam_frame.setObjectName("camera_frame")
        cam_frame_layout = QVBoxLayout(self.cam_frame)
        cam_frame_layout.setContentsMargins(0, 0, 0, 0)

        self.cam_label = QLabel("NO CAMERA SIGNAL")
        self.cam_label.setObjectName("camera_placeholder")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setMinimumSize(540, 380)
        self.cam_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cam_frame_layout.addWidget(self.cam_label)
        left_layout.addWidget(self.cam_frame)

        # Detected gesture banner
        detected_row = QHBoxLayout()
        det_lbl = QLabel("NOW SEEING:")
        det_lbl.setObjectName("muted")
        detected_row.addWidget(det_lbl)
        self.detected_label = QLabel("---")
        self.detected_label.setStyleSheet(
            "color:#00b4d8; font-weight:700; font-size:13px; letter-spacing:3px;"
        )
        detected_row.addWidget(self.detected_label)
        detected_row.addStretch()

        self.frame_count_lbl = QLabel("FRAMES: 0")
        self.frame_count_lbl.setObjectName("muted")
        detected_row.addWidget(self.frame_count_lbl)
        left_layout.addLayout(detected_row)

        root.addWidget(left, 3)

        # ═══ RIGHT: Record panel ══════════════════════════════════════════════
        right = QWidget()
        right.setObjectName("content_area")
        right.setFixedWidth(360)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 28, 30, 28)
        right_layout.setSpacing(0)

        # Label input
        label_lbl = QLabel("GESTURE LABEL")
        label_lbl.setObjectName("h3")
        right_layout.addWidget(label_lbl)
        right_layout.addSpacing(10)

        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("e.g. CUSTOM_WAVE, CIRCLE...")
        right_layout.addWidget(self.label_input)
        right_layout.addSpacing(18)

        # Gesture type
        type_lbl = QLabel("GESTURE TYPE")
        type_lbl.setObjectName("h3")
        right_layout.addWidget(type_lbl)
        right_layout.addSpacing(10)

        type_row = QHBoxLayout()
        self.static_radio  = QRadioButton("STATIC")
        self.dynamic_radio = QRadioButton("DYNAMIC")
        self.static_radio.setChecked(True)

        type_group = QButtonGroup(self)
        type_group.addButton(self.static_radio)
        type_group.addButton(self.dynamic_radio)

        type_row.addWidget(self.static_radio)
        type_row.addSpacing(20)
        type_row.addWidget(self.dynamic_radio)
        type_row.addStretch()
        right_layout.addLayout(type_row)

        right_layout.addSpacing(10)

        # Type explanation
        self.type_hint = QLabel(
            "STATIC: Single hand pose (e.g. fist, open palm)\n"
            "DYNAMIC: Movement-based (e.g. swipe, wave)"
        )
        self.type_hint.setStyleSheet(
            "color:#1e3a5f; font-size:10px; line-height:180%; letter-spacing:1px;"
        )
        right_layout.addWidget(self.type_hint)
        right_layout.addSpacing(24)

        # Record button
        self.record_btn = QPushButton("● START RECORDING")
        self.record_btn.setObjectName("danger_btn")
        self.record_btn.setCursor(Qt.PointingHandCursor)
        self.record_btn.clicked.connect(self._toggle_recording)
        right_layout.addWidget(self.record_btn)

        right_layout.addSpacing(8)

        # Progress bar (custom)
        self.progress_frame = QFrame()
        self.progress_frame.setFixedHeight(4)
        self.progress_frame.setStyleSheet(
            "background:#0f1929; border-radius:2px;"
        )
        right_layout.addWidget(self.progress_frame)

        self.progress_bar = QFrame(self.progress_frame)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setFixedWidth(0)
        self.progress_bar.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #ef4444, stop:1 #f72585); border-radius:2px;"
        )

        right_layout.addSpacing(24)
        right_layout.addWidget(self._divider())
        right_layout.addSpacing(20)

        # Saved gestures
        saved_header = QHBoxLayout()
        saved_lbl = QLabel("SAVED GESTURES")
        saved_lbl.setObjectName("h3")
        saved_header.addWidget(saved_lbl)
        saved_header.addStretch()
        self.count_lbl = QLabel("0 GESTURES")
        self.count_lbl.setObjectName("muted")
        saved_header.addWidget(self.count_lbl)
        right_layout.addLayout(saved_header)
        right_layout.addSpacing(10)

        self.gestures_list = QListWidget()
        right_layout.addWidget(self.gestures_list, 1)
        right_layout.addSpacing(10)

        del_btn = QPushButton("DELETE SELECTED")
        del_btn.setObjectName("ghost_btn")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self._delete_selected)
        right_layout.addWidget(del_btn)

        root.addWidget(right, 0)

        # Timer for recording progress
        self._rec_timer    = QTimer(self)
        self._rec_timer.timeout.connect(self._rec_tick)
        self._rec_frames   = 0
        self._rec_max      = 90  # ~3 seconds at 30fps

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    # ── Signals ───────────────────────────────────────────────────────────────
    def _connect_signals(self):
        self.cam_thread.frame_signal.connect(self._on_frame)
        self.cam_thread.gesture_signal.connect(self._on_gesture)

    def _on_frame(self, qimg):
        pix = QPixmap.fromImage(qimg)
        self.cam_label.setPixmap(
            pix.scaled(self.cam_label.size(), Qt.KeepAspectRatio,
                       Qt.SmoothTransformation)
        )

    def _on_gesture(self, displayed: str, triggered: str,
                    confidence: float = 0.0, processing_ms: float = 0.0):
        self._current_detected = displayed
        meta = GESTURE_META.get(displayed, GESTURE_META["NONE"])
        name = meta.get("desc", "").upper() if displayed not in ("NONE", "") else "---"
        color = meta.get("color", "#1e3a5f")
        self.detected_label.setText(name)
        self.detected_label.setStyleSheet(
            f"color:{color}; font-weight:700; font-size:13px; letter-spacing:3px;"
        )

        if self._recording:
            self._record_data.append(displayed)

    # ── Record ────────────────────────────────────────────────────────────────
    def _toggle_recording(self):
        if not self._recording:
            label = self.label_input.text().strip()
            if not label:
                QMessageBox.warning(self, "Label Required",
                                    "Please enter a gesture label before recording.")
                return
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        self._recording   = True
        self._record_data = []
        self._rec_frames  = 0
        self.record_btn.setText("■  STOP RECORDING")
        self.record_btn.setObjectName("primary_btn")
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.rec_status.setText("● RECORDING IN PROGRESS...")
        self.rec_status.setStyleSheet(
            "color:#ef4444; font-size:12px; font-weight:600; letter-spacing:2px;"
        )
        self.cam_frame.setObjectName("camera_frame_active")
        self.cam_frame.style().unpolish(self.cam_frame)
        self.cam_frame.style().polish(self.cam_frame)
        self._rec_timer.start(33)  # ~30fps ticks

    def _stop_recording(self):
        self._recording = False
        self._rec_timer.stop()
        self.record_btn.setText("● START RECORDING")
        self.record_btn.setObjectName("danger_btn")
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.rec_status.setText("RECORDING SAVED")
        self.rec_status.setStyleSheet(
            "color:#06d6a0; font-size:12px; font-weight:600; letter-spacing:2px;"
        )
        self.cam_frame.setObjectName("camera_frame")
        self.cam_frame.style().unpolish(self.cam_frame)
        self.cam_frame.style().polish(self.cam_frame)
        self.progress_bar.setFixedWidth(0)

        if self._record_data:
            self._save_gesture()

        QTimer.singleShot(2000, lambda: self.rec_status.setText(
            "STANDBY — POSITION YOUR HAND"
        ))
        QTimer.singleShot(2000, lambda: self.rec_status.setStyleSheet(
            "color:#334155; font-size:12px; font-weight:600; letter-spacing:2px;"
        ))

    def _rec_tick(self):
        self._rec_frames += 1
        self.frame_count_lbl.setText(f"FRAMES: {self._rec_frames}")

        # Update progress bar
        progress_width = int(
            (self._rec_frames / self._rec_max) *
            self.progress_frame.width()
        )
        self.progress_bar.setFixedWidth(min(progress_width, self.progress_frame.width()))

        # Auto-stop after max frames
        if self._rec_frames >= self._rec_max:
            self._stop_recording()

    def _save_gesture(self):
        label = self.label_input.text().strip()
        gtype = "static" if self.static_radio.isChecked() else "dynamic"

        # Count most frequent gesture in recording
        from collections import Counter
        counts = Counter(
            g for g in self._record_data if g not in ("NONE", "UNKNOWN")
        )
        dominant = counts.most_common(1)[0][0] if counts else "UNKNOWN"

        record = {
            "id":        datetime.now().strftime("%Y%m%d_%H%M%S"),
            "label":     label,
            "type":      gtype,
            "dominant":  dominant,
            "frames":    self._rec_frames,
            "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.recordings.append(record)
        self._save_recordings()
        self._refresh_list()

    # ── List ──────────────────────────────────────────────────────────────────
    def _refresh_list(self):
        self.gestures_list.clear()
        for rec in reversed(self.recordings):
            gtype   = rec.get("type", "static").upper()
            label   = rec.get("label", "UNKNOWN")
            dominant = rec.get("dominant", "?")
            ts      = rec.get("recorded_at", "")
            frames  = rec.get("frames", 0)

            text = f"{label}  [{gtype}]  ·  {dominant}  ·  {frames}f  ·  {ts}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, rec["id"])
            color = "#a855f7" if gtype == "DYNAMIC" else "#00b4d8"
            item.setForeground(QColor(color))
            self.gestures_list.addItem(item)

        self.count_lbl.setText(f"{len(self.recordings)} GESTURES")

    def _delete_selected(self):
        item = self.gestures_list.currentItem()
        if not item:
            return
        rid = item.data(Qt.UserRole)
        self.recordings = [r for r in self.recordings if r["id"] != rid]
        self._save_recordings()
        self._refresh_list()

    def on_activated(self):
        self.cam_thread.set_mode(CameraThread.MODE_RECORD)
        self._refresh_list()

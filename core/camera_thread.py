import cv2
import numpy as np
import os
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui  import QImage
from PyQt5.QtWidgets import QApplication

from core.gesture_engine import GestureEngine
from core.action_mapper  import ActionMapper


class CameraThread(QThread):
    """Background thread: captures camera → gesture detection → emits signals."""

    frame_signal   = pyqtSignal(QImage)          # current video frame
    gesture_signal = pyqtSignal(str, str, float, float)
    calibration_complete = pyqtSignal(float, float, float, float)
    error_signal   = pyqtSignal(str)

    MODE_IDLE    = "idle"
    MODE_CONTROL = "control"
    MODE_RECORD  = "record"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.camera_index        = 0
        self.mode                = self.MODE_IDLE
        self.draw_landmarks      = True
        self.cursor_enabled      = True
        self.volume_enabled      = True
        self.click_enabled       = False
        self.control_unlocked    = False
        self._last_hand_seen     = 0.0
        self._unlock_timeout     = 2.0
        self._calibration_samples = []
        self._calibrating = False
        self.detection_confidence = 0.7
        self.tracking_confidence = 0.5
        self.action_confidence = 0.65
        self._running            = False
        self.action_mapper: ActionMapper | None = None
        self.engine: GestureEngine | None       = None

    # ── Control ───────────────────────────────────────────────────────────────
    def set_mode(self, mode: str):
        self.mode = mode

    def set_camera_index(self, idx: int):
        self.camera_index = idx

    def set_action_mapper(self, mapper: ActionMapper):
        self.action_mapper = mapper

    def set_cursor_enabled(self, enabled: bool):
        self.cursor_enabled = bool(enabled)

    def set_volume_enabled(self, enabled: bool):
        self.volume_enabled = bool(enabled)

    def set_click_enabled(self, enabled: bool):
        self.click_enabled = bool(enabled)
        if not self.click_enabled and self.action_mapper:
            self.action_mapper.release_drag()

    def set_control_enabled(self, enabled: bool):
        self.control_unlocked = False
        if not enabled and self.action_mapper:
            self.action_mapper.release_drag()

    def set_confidence(self, detection: float, tracking: float = 0.5):
        self.detection_confidence = float(detection)
        self.tracking_confidence = float(tracking)
        if self.engine:
            self.engine.set_confidence(
                self.detection_confidence, self.tracking_confidence
            )
            self.engine.set_min_action_confidence(self.action_confidence)

    def start_calibration(self):
        self._calibration_samples = []
        self._calibrating = True

    def _record_calibration_point(self, landmarks):
        if not self._calibrating or landmarks is None:
            return
        self._calibration_samples.append((float(landmarks[8][0]), float(landmarks[8][1])))
        if len(self._calibration_samples) < 60:
            return
        points = np.asarray(self._calibration_samples, dtype=np.float32)
        left, top = np.percentile(points, 5, axis=0)
        right, bottom = np.percentile(points, 95, axis=0)
        self._calibrating = False
        self._calibration_samples = []
        self.calibration_complete.emit(float(left), float(top), float(right), float(bottom))

    def _draw_hud_overlay(self, frame, displayed, confidence, processing_ms):
        h, w, _ = frame.shape

        # Bounding box around hand & pointer reticle
        if self.engine and self.engine.last_image_landmarks is not None:
            lms = self.engine.last_image_landmarks
            pts_x = (lms[:, 0] * w).astype(int)
            pts_y = (lms[:, 1] * h).astype(int)
            min_x, max_x = max(0, np.min(pts_x) - 15), min(w, np.max(pts_x) + 15)
            min_y, max_y = max(0, np.min(pts_y) - 15), min(h, np.max(pts_y) + 15)

            bbox_color = (216, 180, 0) if self.control_unlocked else (68, 68, 239)
            cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), bbox_color, 1)

            # Corner brackets
            length = 15
            for cx, cy in [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]:
                dx = 1 if cx == min_x else -1
                dy = 1 if cy == min_y else -1
                cv2.line(frame, (cx, cy), (cx + dx * length, cy), bbox_color, 2)
                cv2.line(frame, (cx, cy), (cx, cy + dy * length), bbox_color, 2)

            # Target reticle on index fingertip when pointing/pinching
            if displayed in ("POINT", "PINCH"):
                ix, iy = pts_x[8], pts_y[8]
                cv2.circle(frame, (ix, iy), 10, (247, 37, 245), 2)
                cv2.circle(frame, (ix, iy), 2, (247, 37, 245), -1)
                cv2.line(frame, (ix - 14, iy), (ix + 14, iy), (247, 37, 245), 1)
                cv2.line(frame, (ix, iy - 14), (ix, iy + 14), (247, 37, 245), 1)

        # Top HUD bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (8, 8), (w - 8, 42), (16, 11, 8), -1)
        cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

        lock_status = "UNLOCKED" if self.control_unlocked else "LOCKED (Show Palm)"
        status_color = (160, 214, 6) if self.control_unlocked else (68, 68, 239)
        cv2.putText(frame, f"STATUS: {lock_status}", (16, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1, cv2.LINE_AA)

        if displayed not in ("NONE", ""):
            cv2.putText(frame, f"GESTURE: {displayed}", (250, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (216, 180, 0), 1, cv2.LINE_AA)

        cv2.putText(frame, f"{processing_ms:.0f}ms", (w - 80, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

    def stop(self):
        self._running = False
        self.wait(3000)

    # ── Thread entry ──────────────────────────────────────────────────────────
    def _open_camera(self):
        backends = [cv2.CAP_ANY]
        if os.name == "nt":
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            cap = cv2.VideoCapture(self.camera_index, backend)
            if cap.isOpened():
                return cap
            cap.release()
        return None

    def run(self):
        self._running = True
        self.engine   = GestureEngine(
            detection_confidence=self.detection_confidence,
            tracking_confidence=self.tracking_confidence,
        )
        self.engine.set_min_action_confidence(self.action_confidence)

        cap = None
        read_failures = 0
        profile_check_frame = 0

        while self._running:
            if self.mode == self.MODE_IDLE:
                if cap is not None:
                    cap.release()
                    cap = None
                time.sleep(0.05)
                continue

            if cap is None:
                cap = self._open_camera()
                if cap is None and self.camera_index != 0:
                    original_index = self.camera_index
                    self.camera_index = 0
                    cap = self._open_camera()
                    self.camera_index = original_index
                if cap is None:
                    self.error_signal.emit("Could not open camera. Check Settings or close other camera apps.")
                    time.sleep(0.5)
                    continue
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)

            ret, frame = cap.read()
            if not ret:
                read_failures += 1
                if read_failures >= 15:
                    if cap is not None:
                        cap.release()
                        cap = None
                    self.error_signal.emit("Camera feed interrupted. Attempting reconnect...")
                    read_failures = 0
                time.sleep(0.03)
                continue
            read_failures = 0
            profile_check_frame += 1
            if profile_check_frame >= 30 and self.action_mapper:
                self.action_mapper.refresh_application_profile()
                profile_check_frame = 0

            frame = cv2.flip(frame, 1)   # mirror (feels natural)

            displayed  = "NONE"
            triggered  = None
            processing_ms = 0.0

            if self.mode != self.MODE_IDLE and self.engine:
                started_at = time.perf_counter()
                frame, displayed, triggered = self.engine.process_frame(
                    frame,
                    draw_landmarks=self.draw_landmarks
                )
                processing_ms = (time.perf_counter() - started_at) * 1000.0

                now = time.monotonic()
                if displayed not in ("NONE", "UNKNOWN"):
                    self._last_hand_seen = now
                elif now - self._last_hand_seen >= self._unlock_timeout:
                    self.control_unlocked = False
                    if self.action_mapper:
                        self.action_mapper.release_drag()

                if (self.mode == self.MODE_CONTROL and not self.control_unlocked
                        and displayed == "OPEN_PALM"):
                    self.control_unlocked = True
                    triggered = None

                if (triggered and self.mode == self.MODE_CONTROL
                        and self.control_unlocked and self.action_mapper):
                    self.action_mapper.execute(triggered)

                if self.action_mapper and self.engine.last_normalized_landmarks is not None:
                    landmarks = self.engine.last_normalized_landmarks
                    self._record_calibration_point(self.engine.last_image_landmarks)
                    pointer_active = displayed in ("POINT", "PINCH")
                    if (self.cursor_enabled and self.control_unlocked
                            and pointer_active):
                        primary_screen = QApplication.primaryScreen()
                        if primary_screen:
                            screen = primary_screen.geometry()
                            image_landmarks = self.engine.last_image_landmarks
                            self.action_mapper.update_cursor(
                                float(image_landmarks[8][0]),
                                float(image_landmarks[8][1]),
                                screen.width(), screen.height(),
                            )
                    pinch_distance = float(np.linalg.norm(landmarks[4] - landmarks[8]))
                    self.action_mapper.update_volume(
                        pinch_distance,
                        active=(self.volume_enabled and self.control_unlocked
                                and displayed == "PINCH"
                                and self.mode == self.MODE_CONTROL),
                    )
                    self.action_mapper.set_dragging(
                        self.click_enabled and self.control_unlocked
                        and displayed == "PINCH"
                    )
            elif self.action_mapper:
                self.action_mapper.update_volume(0.0, active=False)
                self.action_mapper.release_drag()

            # Draw Cyberpunk HUD overlay
            if self.mode != self.MODE_IDLE:
                self._draw_hud_overlay(frame, displayed, confidence, processing_ms)

            # Convert frame → QImage
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888).copy()
            self.frame_signal.emit(qimg)

        cap.release()
        if self.engine:
            self.engine.release()
            self.engine = None

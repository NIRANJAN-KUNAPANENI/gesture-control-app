import csv
import cv2
import numpy as np
import os
import time
from collections import deque

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
import mediapipe as mp

# Gesture display info: icon + accent color
GESTURE_META = {
    "OPEN_PALM":   {"icon": "[PALM]",  "color": "#00b4d8", "desc": "Open Palm"},
    "FIST":        {"icon": "[FIST]",  "color": "#ef4444", "desc": "Fist"},
    "THUMBS_UP":   {"icon": "[UP]",    "color": "#06d6a0", "desc": "Thumbs Up"},
    "THUMBS_DOWN": {"icon": "[DOWN]",  "color": "#f59e0b", "desc": "Thumbs Down"},
    "PEACE":       {"icon": "[V]",     "color": "#a855f7", "desc": "Peace / V"},
    "POINT":       {"icon": "[POINT]", "color": "#f72585", "desc": "Point"},
    "PINCH":       {"icon": "[PINCH]", "color": "#f59e0b", "desc": "Pinch / Volume"},
    "OK_SIGN":     {"icon": "[OK]",    "color": "#06d6a0", "desc": "OK Sign"},
    "ROCK_ON":     {"icon": "[ROCK]",  "color": "#f72585", "desc": "Rock / Horns"},
    "CALL_ME":     {"icon": "[CALL]",  "color": "#a855f7", "desc": "Call Me"},
    "THREE":       {"icon": "[III]",   "color": "#00b4d8", "desc": "Three Fingers"},
    "FOUR":        {"icon": "[IV]",    "color": "#00b4d8", "desc": "Four Fingers"},
    "SWIPE_LEFT":  {"icon": "[<--]",   "color": "#00b4d8", "desc": "Swipe Left"},
    "SWIPE_RIGHT": {"icon": "[-->]",   "color": "#00b4d8", "desc": "Swipe Right"},
    "SWIPE_UP":    {"icon": "[^]",     "color": "#00b4d8", "desc": "Swipe Up"},
    "SWIPE_DOWN":  {"icon": "[v]",     "color": "#00b4d8", "desc": "Swipe Down"},
    "UNKNOWN":     {"icon": "[?]",     "color": "#334155", "desc": "Unknown"},
    "NONE":        {"icon": "",        "color": "#080b14", "desc": ""},
}


class GestureEngine:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.5,
                 debounce_frames=5, model_path=None, label_path=None):
        self.mp_hands  = mp.solutions.hands
        self.mp_draw   = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        # Motion tracking for swipes
        self.wrist_history: deque = deque(maxlen=20)
        self.last_triggered_time: float = 0.0
        self.cooldown: float = 0.3
        self.last_triggered: str = ""
        self.debounce_frames = max(5, int(debounce_frames))
        self._gesture_buffer: deque = deque(maxlen=self.debounce_frames)
        self._stable_gesture = "NONE"
        self._gesture_armed = True
        self.last_normalized_landmarks = None
        self.last_image_landmarks = None
        self.last_confidence = 0.0
        self.min_action_confidence = 0.65
        self.labels = []
        self.interpreter = None
        model_path = model_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "models", "keypoint_classifier.tflite",
        )
        label_path = label_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "models", "keypoint_classifier_label.csv",
        )
        self._load_classifier(model_path, label_path)

    def _load_classifier(self, model_path, label_path):
        try:
            import tensorflow as tf
            with open(label_path, encoding="utf-8-sig") as labels_file:
                self.labels = [row[0] for row in csv.reader(labels_file) if row]
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        except Exception:
            self.interpreter = None

    @staticmethod
    def _model_features(image_landmarks):
        points = np.rint(image_landmarks[:, :2]).astype(np.float32)
        points -= points[0]
        flattened = points.reshape(-1)
        scale = float(np.max(np.abs(flattened)))
        return flattened / scale if scale >= 1e-6 else flattened

    def _infer_model_gesture(self, image_landmarks):
        if self.interpreter is None:
            return None
        flattened = self._model_features(image_landmarks)
        input_index = self.input_details[0]["index"]
        self.interpreter.set_tensor(input_index, np.array([flattened]))
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        scores = np.squeeze(output)
        gesture_id = int(np.argmax(scores))
        self.last_confidence = float(scores[gesture_id])
        return self.labels[gesture_id] if gesture_id < len(self.labels) else None

    @staticmethod
    def normalize_landmarks(landmarks):
        """Translate landmarks to the wrist and scale by wrist-to-middle MCP."""
        coordinates = np.asarray(
            [[point.x, point.y, point.z] for point in landmarks],
            dtype=np.float32,
        )
        if coordinates.shape != (21, 3):
            raise ValueError("MediaPipe must provide exactly 21 hand landmarks")
        translated = coordinates - coordinates[0]
        scale = float(np.linalg.norm(translated[9]))
        return translated / scale if scale >= 1e-6 else np.zeros_like(translated)

    # ── Finger state ──────────────────────────────────────────────────────────
    def _finger_states(self, lm, hand_label: str):
        """Return [thumb, index, middle, ring, pinky] booleans (True = extended)."""
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        extended = []

        # Thumb: compare x-axis (mirrored feed considered)
        if hand_label == "Right":
            extended.append(lm[tips[0]][0] < lm[pips[0]][0])
        else:
            extended.append(lm[tips[0]][0] > lm[pips[0]][0])

        # Other fingers: compare y-axis (smaller y = higher in image = extended)
        for i in range(1, 5):
            extended.append(lm[tips[i]][1] < lm[pips[i]][1])

        return extended

    # ── Swipe detection ───────────────────────────────────────────────────────
    def _detect_swipe(self):
        if len(self.wrist_history) < 10:
            return None
        pts = list(self.wrist_history)
        dx  = pts[-1][0] - pts[0][0]
        dy  = pts[-1][1] - pts[0][1]

        THRESH = 0.18
        if abs(dx) > abs(dy) and abs(dx) > THRESH:
            return "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"
        if abs(dy) > abs(dx) and abs(dy) > THRESH:
            return "SWIPE_DOWN"  if dy > 0 else "SWIPE_UP"
        return None

    # ── Static gesture classifier ─────────────────────────────────────────────
    def _classify_static(self, lm, hand_label: str):
        t, i, m, r, p = self._finger_states(lm, hand_label)
        total = sum([t, i, m, r, p])
        thumb_index_dist = float(np.linalg.norm(lm[4] - lm[8]))

        # OK Sign: Thumb and Index tips touch, Middle/Ring/Pinky extended
        if thumb_index_dist < 0.38 and (m and r and p):
            return "OK_SIGN"

        # Pinch: Thumb and Index near each other, other fingers folded
        if thumb_index_dist < 0.42 and not (m or r or p):
            return "PINCH"

        if total == 5:
            return "OPEN_PALM"
        if total == 0:
            return "FIST"

        # Rock / Devil Horns: Index + Pinky extended, Middle + Ring folded
        if i and p and not m and not r:
            return "ROCK_ON"

        # Call Me: Thumb + Pinky extended, Index + Middle + Ring folded
        if t and p and not i and not m and not r:
            return "CALL_ME"

        if t and not i and not m and not r and not p:
            # Thumb only — up or down?
            return "THUMBS_UP" if lm[4][1] < 0 else "THUMBS_DOWN"

        if not t and i and m and not r and not p:
            return "PEACE"
        if not t and i and not m and not r and not p:
            return "POINT"
        if not t and i and m and r and not p:
            return "THREE"
        if not t and i and m and r and p:
            return "FOUR"

        return "UNKNOWN"

    # ── Main process method ───────────────────────────────────────────────────
    def process_frame(self, frame, draw_landmarks=True):
        """
        Returns:
            annotated_frame (np.ndarray)
            displayed_gesture (str)  – what's currently seen  (for UI label)
            triggered_gesture (str)  – what fired an action   (subject to cooldown)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        displayed  = "NONE"
        triggered  = None
        self.last_confidence = 0.0

        if results.multi_hand_landmarks:
            for hand_lm, handedness_info in zip(
                results.multi_hand_landmarks,
                results.multi_handedness,
            ):
                hand_label = handedness_info.classification[0].label

                if draw_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_lm,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style(),
                    )

                lm = self.normalize_landmarks(hand_lm.landmark)
                self.last_normalized_landmarks = lm
                self.last_image_landmarks = np.asarray(
                    [[point.x, point.y, point.z] for point in hand_lm.landmark],
                    dtype=np.float32,
                )
                self.wrist_history.append((
                    float(hand_lm.landmark[0].x),
                    float(hand_lm.landmark[0].y),
                ))

                swipe = self._detect_swipe()
                if swipe:
                    displayed = swipe
                    self.wrist_history.clear()
                else:
                    displayed = self._classify_static(lm, hand_label)
                    self.last_confidence = 0.85
                    model_gesture = self._infer_model_gesture(self.last_image_landmarks)
                    if model_gesture == "Open":
                        displayed = "OPEN_PALM"
                    elif model_gesture == "Close":
                        displayed = "FIST"
                    elif model_gesture == "Pointer":
                        displayed = "POINT"
        else:
            self.wrist_history.clear()
            self.last_normalized_landmarks = None
            self.last_image_landmarks = None
            displayed = "NONE"

        self._gesture_buffer.append(displayed)
        if (len(self._gesture_buffer) == self.debounce_frames
                and len(set(self._gesture_buffer)) == 1):
            stable = self._gesture_buffer[-1]
            if stable != self._stable_gesture:
                self._stable_gesture = stable
                if stable == "NONE":
                    self._gesture_armed = True
                elif stable not in ("UNKNOWN", "NONE") and self._gesture_armed:
                    now = time.monotonic()
                    if (now - self.last_triggered_time >= self.cooldown
                            and self.last_confidence >= self.min_action_confidence):
                        triggered = stable
                        self.last_triggered_time = now
                        self.last_triggered = stable
                        self._gesture_armed = False

        displayed = self._stable_gesture if self._stable_gesture != "NONE" else displayed

        return frame, displayed, triggered

    def set_cooldown(self, seconds: float):
        self.cooldown = max(0.3, float(seconds))

    def set_min_action_confidence(self, confidence: float):
        self.min_action_confidence = min(1.0, max(0.0, float(confidence)))

    def set_confidence(self, detection: float, tracking: float):
        self.hands.close()
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detection,
            min_tracking_confidence=tracking,
        )

    def release(self):
        self.hands.close()

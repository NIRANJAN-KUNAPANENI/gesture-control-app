import unittest
from types import SimpleNamespace
import numpy as np

from core.action_mapper import ActionMapper, OneEuroFilter
from core.gesture_engine import GestureEngine, GESTURE_META


class GestureCoreTests(unittest.TestCase):
    def test_landmarks_are_wrist_relative_and_unit_scaled(self):
        landmarks = [
            SimpleNamespace(x=float(index) * 0.02, y=float(index) * 0.01, z=0.0)
            for index in range(21)
        ]
        normalized = GestureEngine.normalize_landmarks(landmarks)
        self.assertTrue(np.allclose(normalized[0], [0.0, 0.0, 0.0]))
        self.assertAlmostEqual(float(np.linalg.norm(normalized[9])), 1.0)

    def test_model_features_have_42_values(self):
        points = np.arange(63, dtype=np.float32).reshape(21, 3)
        features = GestureEngine._model_features(points)
        self.assertEqual(features.shape, (42,))
        self.assertAlmostEqual(float(features[0]), 0.0)

    def test_cursor_settings_are_clamped(self):
        mapper = ActionMapper("missing-presets.json")
        mapper.set_cursor_alpha(2.0)
        mapper.set_cursor_bounds(-1.0, -1.0, 2.0, 2.0)
        self.assertEqual(mapper.cursor_alpha, 1.0)
        self.assertEqual(mapper.cursor_bounds, (0.0, 0.0, 1.0, 1.0))

    def test_one_euro_filter_adaptive_smoothing(self):
        euro = OneEuroFilter(min_cutoff=0.8, beta=0.008)
        val1 = euro.filter(0.1, timestamp=0.0)
        val2 = euro.filter(0.12, timestamp=0.033)
        val3 = euro.filter(0.90, timestamp=0.066)
        self.assertEqual(val1, 0.1)
        self.assertTrue(0.1 < val2 < 0.12)
        self.assertTrue(val3 > val2)

    def test_new_gestures_meta_registered(self):
        for key in ["OK_SIGN", "ROCK_ON", "CALL_ME", "FOUR"]:
            self.assertIn(key, GESTURE_META)
            self.assertIn("desc", GESTURE_META[key])


if __name__ == "__main__":
    unittest.main()

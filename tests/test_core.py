import unittest
from types import SimpleNamespace

import numpy as np

from core.action_mapper import ActionMapper
from core.gesture_engine import GestureEngine


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


if __name__ == "__main__":
    unittest.main()

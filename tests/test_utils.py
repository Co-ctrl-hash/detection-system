"""Unit tests for utility functions."""
from __future__ import annotations

import unittest
from src.utils import yolo_label_to_box


class TestUtils(unittest.TestCase):
    
    def test_yolo_label_to_box_center(self):
        """Test YOLO format conversion for centered box."""
        # normalized: xc=0.5, yc=0.5, w=0.2, h=0.3 in 100x100 image
        x1, y1, x2, y2 = yolo_label_to_box(0.5, 0.5, 0.2, 0.3, 100, 100)
        self.assertAlmostEqual(x1, 40.0)
        self.assertAlmostEqual(y1, 35.0)
        self.assertAlmostEqual(x2, 60.0)
        self.assertAlmostEqual(y2, 65.0)
    
    def test_yolo_label_to_box_corner(self):
        """Test YOLO format conversion for corner box."""
        # normalized: xc=0.1, yc=0.1, w=0.2, h=0.2 in 200x200 image
        x1, y1, x2, y2 = yolo_label_to_box(0.1, 0.1, 0.2, 0.2, 200, 200)
        self.assertAlmostEqual(x1, 0.0)
        self.assertAlmostEqual(y1, 0.0)
        self.assertAlmostEqual(x2, 40.0)
        self.assertAlmostEqual(y2, 40.0)


if __name__ == "__main__":
    unittest.main()

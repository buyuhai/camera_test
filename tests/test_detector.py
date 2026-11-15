import cv2
import numpy as np
import pytest

from hough_gui.core.detector import detect_circles
from hough_gui.core.params import HoughParams

EXPECTED = [(160.0, 160.0, 40.0), (400.0, 120.0, 60.0), (320.0, 360.0, 80.0)]


def synthetic_grayscale() -> np.ndarray:
    image = np.zeros((480, 640), dtype=np.uint8)
    for x, y, r in EXPECTED:
        cv2.circle(image, (int(x), int(y)), int(r), 255, -1, lineType=cv2.LINE_AA)
    return image


def assert_matches(found, expected, coord_tol, radius_tol):
    assert len(found) == len(expected), f"检出 {len(found)} 个圆，期望 {len(expected)} 个"
    remaining = list(found)
    for ex, ey, er in expected:
        best = min(remaining, key=lambda c: abs(c.x - ex) + abs(c.y - ey))
        assert abs(best.x - ex) <= coord_tol, f"圆心 x={best.x} 偏离 {ex}"
        assert abs(best.y - ey) <= coord_tol, f"圆心 y={best.y} 偏离 {ey}"
        assert abs(best.r - er) <= radius_tol, f"半径 {best.r} 偏离 {er}"
        remaining.remove(best)


def test_detects_three_synthetic_circles():
    found = detect_circles(synthetic_grayscale(), HoughParams())
    assert_matches(found, EXPECTED, coord_tol=2, radius_tol=2)


def test_blank_image_returns_empty_list():
    blank = np.zeros((480, 640), dtype=np.uint8)
    assert detect_circles(blank, HoughParams()) == []


def test_bgr_and_gray_inputs_agree():
    gray = synthetic_grayscale()
    bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    from_gray = detect_circles(gray, HoughParams())
    from_bgr = detect_circles(bgr, HoughParams())
    assert_matches(from_bgr, [(c.x, c.y, c.r) for c in from_gray], coord_tol=1, radius_tol=1)


def test_invalid_params_raise_value_error():
    with pytest.raises(ValueError, match="dp"):
        detect_circles(synthetic_grayscale(), HoughParams(dp=0))

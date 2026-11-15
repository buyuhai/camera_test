import os

import cv2
import numpy as np
import pytest

from hough_gui.core.detector import Circle
from hough_gui.core.imageio import load_image, render_overlay, save_annotated

CIRCLES = [(160.0, 160.0, 40.0), (400.0, 120.0, 60.0), (320.0, 360.0, 80.0)]


def synthetic_bgr() -> np.ndarray:
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    for x, y, r in CIRCLES:
        cv2.circle(image, (int(x), int(y)), int(r), (255, 255, 255), -1, lineType=cv2.LINE_AA)
    return image


def write_png(path, image):
    ok, encoded = cv2.imencode(".png", image)
    assert ok
    encoded.tofile(str(path))


def test_load_png_with_chinese_path(tmp_path):
    target = tmp_path / "测试图片 圆圈.png"
    write_png(target, synthetic_bgr())

    loaded = load_image(str(target))

    assert loaded.shape == (480, 640, 3)
    assert np.array_equal(loaded, synthetic_bgr())


def test_load_non_image_raises_value_error(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("不是图片", encoding="utf-8")

    with pytest.raises(ValueError, match="无法读取图片"):
        load_image(str(target))


def test_load_missing_file_raises_value_error(tmp_path):
    with pytest.raises(ValueError, match="无法读取图片"):
        load_image(str(tmp_path / "不存在.png"))


def test_render_overlay_draws_center_and_keeps_size():
    image = synthetic_bgr()
    circles = [Circle(100.0, 200.0, 30.0)]

    canvas = render_overlay(image, circles)

    assert canvas.shape == image.shape
    assert tuple(int(v) for v in canvas[200, 100]) == (0, 0, 255)
    assert not np.array_equal(canvas, image)


def test_render_overlay_without_circles_is_identity():
    image = synthetic_bgr()

    canvas = render_overlay(image, [])

    assert np.array_equal(canvas, image)


def test_save_annotated_keeps_original_resolution(tmp_path):
    image = render_overlay(synthetic_bgr(), [Circle(160.0, 160.0, 40.0)])
    target = tmp_path / "标注 结果.png"

    save_annotated(str(target), image)

    saved = cv2.imdecode(np.fromfile(str(target), dtype=np.uint8), cv2.IMREAD_COLOR)
    assert saved.shape == (480, 640, 3)
    assert np.array_equal(saved, image)
    assert not os.path.exists(f"{target}.tmp")


def test_save_annotated_failure_keeps_existing_file(tmp_path):
    target = tmp_path / "out" / "结果.png"
    target.parent.mkdir()
    target.write_bytes(b"original")

    os.chmod(target.parent, 0o500)
    try:
        with pytest.raises(Exception):
            save_annotated(str(target), synthetic_bgr())
        assert target.read_bytes() == b"original"
        assert not os.path.exists(f"{target}.tmp")
    finally:
        os.chmod(target.parent, 0o700)

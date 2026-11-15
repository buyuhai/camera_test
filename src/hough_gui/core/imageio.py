"""图片读取、叠加渲染与标注图导出。

读写均走 numpy 缓冲，避免 `cv2.imread`/`cv2.imwrite` 在非 ASCII 路径下失败。
"""

import os

import cv2
import numpy as np

from .detector import Circle

OUTLINE_COLOR = (0, 255, 0)
CENTER_COLOR = (0, 0, 255)
CENTER_MARK_RADIUS = 3


def load_image(path: str) -> np.ndarray:
    """读取图片为 BGR 三通道数组；失败时抛 `ValueError`。"""
    try:
        buffer = np.fromfile(path, dtype=np.uint8)
    except OSError as exc:
        raise ValueError(f"无法读取图片: {path}") from exc
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR) if buffer.size else None
    if image is None:
        raise ValueError(f"无法读取图片: {path}")
    return image


def render_overlay(image: np.ndarray, circles: list[Circle]) -> np.ndarray:
    """在原分辨率副本上绘制圆轮廓与圆心，返回新数组。"""
    canvas = image.copy()
    if not circles:
        return canvas
    height, width = canvas.shape[:2]
    thickness = max(2, round(min(height, width) / 300))
    for circle in circles:
        center = (int(round(circle.x)), int(round(circle.y)))
        cv2.circle(canvas, center, int(round(circle.r)), OUTLINE_COLOR, thickness)
        cv2.circle(canvas, center, CENTER_MARK_RADIUS, CENTER_COLOR, -1)
    return canvas


def save_annotated(path: str, image: np.ndarray) -> None:
    """把 BGR 图像编码为 PNG 并原子替换目标文件。

    先写 `<path>.tmp` 再 `os.replace`，写失败时既有同名文件保持原内容。
    """
    ok, encoded = cv2.imencode(".png", image)
    if not ok:
        raise ValueError(f"无法编码 PNG: {path}")
    tmp_path = f"{path}.tmp"
    try:
        encoded.tofile(tmp_path)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

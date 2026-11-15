"""霍夫圆检测，不依赖 Qt。"""

from typing import NamedTuple

import cv2
import numpy as np

from .params import HoughParams

# 圆心与半径的局部微调：Hough 在纹理丰富的真实照片上常把半径落在内圈边缘，
# 这里以 Hough 结果为初值，在梯度幅值图上找支撑最强的同心圆，使结果贴合真实外沿。
_ANGLE_SAMPLES = 180
_ANGLES = np.linspace(0.0, 2.0 * np.pi, _ANGLE_SAMPLES, endpoint=False)
_COS = np.cos(_ANGLES)
_SIN = np.sin(_ANGLES)
_CENTER_SEARCH_PX = 5
_RADIUS_SEARCH = (0.85, 1.25)
_MIN_VALID_RATIO = 0.6


class Circle(NamedTuple):
    """检出圆：圆心坐标与半径，单位为像素。"""

    x: float
    y: float
    r: float


def _gradient_magnitude(gray: np.ndarray) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    gx = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(blurred, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def _best_circle(
    magnitude: np.ndarray,
    x: float,
    y: float,
    radii: np.ndarray,
    offsets: list[tuple[int, int]],
) -> tuple[int, int, float] | None:
    """在给定圆心偏移与半径集合上，找圆周梯度幅值均值最大的组合。"""
    height, width = magnitude.shape
    min_valid = _ANGLE_SAMPLES * _MIN_VALID_RATIO
    base_x = x + np.outer(radii, _COS)
    base_y = y + np.outer(radii, _SIN)
    best_score = -1.0
    best = None
    for dx, dy in offsets:
        xs = np.rint(base_x + dx).astype(np.int32)
        ys = np.rint(base_y + dy).astype(np.int32)
        inside = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
        values = np.where(
            inside,
            magnitude[np.clip(ys, 0, height - 1), np.clip(xs, 0, width - 1)],
            0.0,
        )
        counts = inside.sum(axis=1)
        scores = np.where(
            counts >= min_valid,
            values.sum(axis=1) / np.maximum(counts, 1),
            -1.0,
        )
        index = int(np.argmax(scores))
        if scores[index] > best_score:
            best_score = float(scores[index])
            best = (dx, dy, float(radii[index]))
    return best


def _refine_circle(magnitude: np.ndarray, circle: Circle, params: HoughParams) -> Circle:
    """先在粗网格上搜索圆心与半径，再在最优解附近细化到 1 px。"""
    height, width = magnitude.shape
    low = max(1.0, float(params.min_radius), circle.r * _RADIUS_SEARCH[0])
    high = min(
        float(params.max_radius) if params.max_radius else float(max(height, width)),
        circle.r * _RADIUS_SEARCH[1],
    )
    if high <= low:
        return circle

    span = range(-_CENTER_SEARCH_PX, _CENTER_SEARCH_PX + 1, 2)
    coarse = _best_circle(
        magnitude,
        circle.x,
        circle.y,
        np.arange(low, high, 2.0),
        [(dx, dy) for dx in span for dy in span],
    )
    if coarse is None:
        return circle

    dx, dy, radius = coarse
    fine_radii = np.arange(max(low, radius - 2.0), min(high, radius + 2.0) + 0.01, 1.0)
    fine = _best_circle(
        magnitude,
        circle.x,
        circle.y,
        fine_radii,
        [(dx + ox, dy + oy) for ox in (-1, 0, 1) for oy in (-1, 0, 1)],
    )
    if fine is None:
        return circle
    dx, dy, radius = fine
    return Circle(circle.x + dx, circle.y + dy, radius)


def detect_circles(image: np.ndarray, params: HoughParams) -> list[Circle]:
    """在 8 位单通道或 BGR 图像上检测圆，返回按发现顺序排列的圆列表。"""
    errors = params.validate()
    if errors:
        raise ValueError("; ".join(errors))

    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    found = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=params.dp,
        minDist=params.min_dist,
        param1=params.param1,
        param2=params.param2,
        minRadius=params.min_radius,
        maxRadius=params.max_radius,
    )
    if found is None:
        return []
    magnitude = _gradient_magnitude(gray)
    circles = [Circle(float(x), float(y), float(r)) for x, y, r in found[0]]
    return [_refine_circle(magnitude, circle, params) for circle in circles]

"""霍夫圆检测，不依赖 Qt。"""

from typing import NamedTuple

import cv2
import numpy as np

from .params import HoughParams


class Circle(NamedTuple):
    """检出圆：圆心坐标与半径，单位为像素。"""

    x: float
    y: float
    r: float


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
    return [Circle(float(x), float(y), float(r)) for x, y, r in found[0]]

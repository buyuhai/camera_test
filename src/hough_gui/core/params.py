"""霍夫圆检测的可调参数。"""

from dataclasses import dataclass


@dataclass
class HoughParams:
    """`cv2.HoughCircles` 的六个可调参数。

    `max_radius` 为 0 表示不限制最大半径（OpenCV 语义），不是半径为 0 的圆。
    """

    dp: float = 1.0
    min_dist: int = 50
    param1: int = 100
    param2: int = 30
    min_radius: int = 0
    max_radius: int = 0

    def validate(self) -> list[str]:
        """返回人类可读的错误列表，空列表表示参数合法。"""
        errors: list[str] = []
        if self.dp <= 0:
            errors.append("dp 必须大于 0")
        if self.min_dist <= 0:
            errors.append("minDist 必须大于 0")
        if self.param1 <= 0:
            errors.append("param1 必须大于 0")
        if self.param2 <= 0:
            errors.append("param2 必须大于 0")
        if self.min_radius < 0:
            errors.append("minRadius 不能为负")
        if self.max_radius < 0:
            errors.append("maxRadius 不能为负")
        if self.max_radius > 0 and self.min_radius > self.max_radius:
            errors.append("minRadius 不能大于 maxRadius")
        return errors

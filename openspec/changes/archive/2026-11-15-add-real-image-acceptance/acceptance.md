# Acceptance

## 规格确认

- 变更：`add-real-image-acceptance`
- 受影响能力：`circle-detection`
- 新增 Requirement：检出半径贴合目标最外沿
- 外沿微调实现提交：`443c86e`
- 验收日期：2026-11-15

## 环境

- 系统：Linux 6.18.58.1-microsoft-standard-WSL2（Ubuntu 24.04）
- Python：3.12.3
- OpenCV：4.6.0
- NumPy：1.26.4
- 检测入口：`hough_gui.core.detector.detect_circles`

## 输入与参数

原始样图只保留在本地 `samples/`，不入库；标注结果图随仓库提交。

| 图片 | 尺寸 | `dp` | `minDist` | `param1` | `param2` | `minRadius` | `maxRadius` |
|---|---|---:|---:|---:|---:|---:|---:|
| `samples/plate.png` | 520×520 | 1.0 | 250 | 100 | 60 | 200 | 0 |
| `samples/coins.jpg` | 760×385 | 1.0 | 250 | 100 | 150 | 120 | 0 |

## 实测结果

| 验收项 | 盘子 | 硬币 |
|---|---|---|
| 检出数量 | 1 | 2 |
| 圆心（px） | (263.5, 256.5) | (192.5, 191.5)、(566.5, 191.5) |
| 半径（px） | 243.3 | 180.0、179.5 |
| 外沿贴合 | 盘子最外沿，径向梯度峰值位于 243.3 px | 两枚硬币外齿圈，径向梯度峰值位于 180.0/179.5 px |
| 误检 | 无 | 无内部人像/花环圆 |

半径与径向梯度峰值位置的偏差均在 2 px 以内，满足规格 Scenario。

## 证据图

- `docs/acceptance/plate_result.png`：绿色轮廓贴合盘子最外沿
- `docs/acceptance/coins_result.png`：两个绿色轮廓分别贴合两枚硬币外齿圈

## 复核命令

```bash
.venv/bin/python - <<'PY'
from hough_gui.core.detector import detect_circles
from hough_gui.core.imageio import load_image
from hough_gui.core.params import HoughParams

cases = [
    ("plate", "samples/plate.png",
     HoughParams(dp=1.0, min_dist=250, param1=100, param2=60,
                 min_radius=200, max_radius=0)),
    ("coins", "samples/coins.jpg",
     HoughParams(dp=1.0, min_dist=250, param1=100, param2=150,
                 min_radius=120, max_radius=0)),
]
for name, path, params in cases:
    circles = detect_circles(load_image(path), params)
    print(name, len(circles),
          [(round(c.x, 1), round(c.y, 1), round(c.r, 1)) for c in circles])
PY
```

预期输出：

```text
plate 1 [(263.5, 256.5, 243.3)]
coins 2 [(192.5, 191.5, 180.0), (566.5, 191.5, 179.5)]
```

## 结论

规格中的硬币外齿圈与盘子外沿两个 Scenario 均通过；检出数量、圆心、半径与证据图一致，验收通过。

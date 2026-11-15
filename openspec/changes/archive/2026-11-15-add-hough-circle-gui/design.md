# Design

## Context

仓库当前只有脚手架：`pyproject.toml`（src 布局，`where = ["src"]`）、`tests/` 与 `src/` 均未创建。运行环境为 Ubuntu 24.04 / ROS 2 Jazzy，`cv2` 4.6.0（apt）与 PyQt5 5.15.10（apt）已存在，venv 以 `--system-site-packages` 创建。项目约束（中文路径 I/O、不用 `cv2.imshow`、检测与 Qt 解耦、合成图像测试）见 `openspec/config.yaml` 的 `context`。

## Goals / Non-Goals

**Goals:**
- 单窗口 PyQt5 应用，检测逻辑纯 NumPy/OpenCV、可在无 GUI 环境下单测。
- 参数改动后自动重检，且不允许陈旧结果覆盖新结果。
- 预览与导出共用同一份原分辨率叠加图，保证「所见即所导出」。

**Non-Goals:**
- 批量处理、视频/相机输入、参数预设保存、撤销/重做、ROS 节点化。
- 检测结果的后处理（圆合并、拟合、亚像素优化）。

## Decisions

### 模块划分
```
src/hough_gui/
├── __init__.py          # __version__
├── __main__.py          # main(): QApplication + MainWindow
├── core/
│   ├── __init__.py
│   ├── params.py        # HoughParams 数据类 + validate()
│   ├── detector.py      # Circle, detect_circles()
│   └── imageio.py       # load_image(), render_overlay(), save_annotated()
└── ui/
    ├── __init__.py
    └── main_window.py   # MainWindow, DetectThread
```
`core/` 不导入任何 `PyQt5` 模块；`ui/` 只做交互与绘制调度。选 `src/` 布局是为防止测试意外导入未安装的包；已有 `pyproject.toml` 的 `packages.find` 依赖它。

### 检测接口
- `params.py`：`@dataclass HoughParams`，字段 `dp: float = 1.0`、`min_dist: int = 50`、`param1: int = 100`、`param2: int = 30`、`min_radius: int = 0`、`max_radius: int = 0`；`validate() -> list[str]` 返回人类可读错误（半径倒置、非正值），空列表表示合法。
- `detector.py`：`Circle = NamedTuple("Circle", [("x", float), ("y", float), ("r", float)])`；`detect_circles(image: np.ndarray, params: HoughParams) -> list[Circle]`；内部 `cv2.cvtColor(..., COLOR_BGR2GRAY)`（单通道输入跳过）、调用 `cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, minDist, param1=..., param2=..., minRadius=..., maxRadius=...)`，`None` 归一化为 `[]`；参数非法时抛 `ValueError("; ".join(errors))`。
- 不把耗时放进 `detect_circles`：耗时由 UI 线程测量（`time.perf_counter()` 包裹后台调用），避免为测试引入时钟依赖。

### 预览与导出一致性
- `render_overlay(image_bgr, circles)` 返回**原分辨率** BGR 副本，用 `cv2.circle` 画轮廓（颜色 `(0, 255, 0)`）与圆心（颜色 `(0, 0, 255)`，半径 3 像素），线宽 `max(2, round(min(h, w) / 300))`；零检出时返回副本本身。
- 窗口持有「当前叠加图」（原分辨率）；预览区用 `QLabel` 承载 `QImage`，显示时 `QPixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)`，在 `resizeEvent` 中重算——保证等比、不留裁剪。
- 导出直接 `cv2.imencode(".png", 叠加图)` + `tofile`，与预览同源，尺寸必然等于原图。
- 备选：`QGraphicsView` + 场景项（可放大平移）——本轮不需要交互式缩放，复杂度更高，未采用；备选：仅在缩放后的 QPixmap 上画圆——会丢失原分辨率细节，且导出需重绘，未采用。

### 线程模型与陈旧结果
- 每次检测请求新建 `DetectThread(QThread)`，构造时接收 `generation: int`、图像副本（`.copy()`）与 `HoughParams`；`run()` 内调用 `detect_circles`，通过 `finished_result(generation, circles, elapsed_ms)` 信号回主线程。
- `MainWindow` 维护 `self._generation`，每次触发检测自增并传给新线程；信号回调中 `if gen != self._generation: return` 丢弃陈旧结果。线程对象存于 `self._detect_thread`，回调末尾 `deleteLater()`。
- 参数变化用 `QTimer`（150 ms，single-shot）防抖：`valueChanged` 只重启计时器，超时后组参数并发起检测。
- `closeEvent` 中若线程仍在运行则 `wait()`，避免「QThread destroyed while running」导致退出崩溃。
- 备选：`QThreadPool + QRunnable`（需自行管理信号对象的生命周期）；备选：`moveToThread` 长驻 worker（需额外队列与取消协议）。单次 QThread 实现最短且满足「不阻塞 + 丢弃陈旧」两个约束。

### 参数控件
- `dp` 用 `QDoubleSpinBox`（1.0–3.0，步长 0.1，1 位小数），其余五个用 `QSpinBox`（`minDist` 1–2000、`param1` 1–500、`param2` 1–200、`minRadius`/`maxRadius` 0–2000）。
- 每个控件 `valueChanged` → 防抖 → 重检；不使用滑块，避免滑块与数值框双控件同步。
- 参数非法时（`HoughParams.validate()` 非空）在参数面板下方以红字显示错误、跳过检测、保留上一次有效预览；点击「打开图片」仍允许。

### 状态栏
- 左侧 `QLabel`（`addPermanentWidget`? 放在普通区域）显示 `图片: <文件名> (<宽>×<高>)`；右侧 `QLabel` 显示 `圆: <n> | 耗时: <ms:.1f> ms`（格式由 spec 固定）。
- 未加载图片时两个标签分别显示「图片: -」「圆: -」。

### 图片 I/O
- `load_image(path: str) -> np.ndarray`：`np.fromfile(path, dtype=np.uint8)` + `cv2.imdecode(..., cv2.IMREAD_COLOR)`；解码失败抛 `ValueError("无法读取图片: <path>")`，UI 用 `QMessageBox.critical` 展示并保持既有状态。
- `save_annotated(path: str, image_bgr: np.ndarray) -> None`：`cv2.imencode(".png", ...)` 编码失败或 `tofile` 抛异常时向上传播；先写同目录临时文件 `path + ".tmp"` 再 `os.replace`，保证失败时不截断既有同名文件。成功/失败后清理临时文件（`try/finally` + `os.path.exists`）。
- 导出默认文件名：原图目录 + 原 stem + `_circles.png`；用户在 `QFileDialog` 中去掉扩展名时自动补 `.png`。
- 备选：`cv2.imread`/`imwrite` 直接读写——在非 ASCII 路径下不可靠，项目约束已排除。

## Risks / Trade-offs

- **大图检测慢（Hough O(像素×半径)）** → 后台线程 + 150 ms 防抖；不降采样（会牺牲精度）。README 标明典型耗时量级。
- **叠加线宽随原图缩放变细** → 线宽按图像短边自适应（`max(2, min(h,w)/300)`）；导出与预览因此保持一致。
- **关闭窗口时检测仍在运行** → `closeEvent` 中 `wait()`；最大等待即一次检测时长，可接受。
- **参数控件步进触发过多检测** → 防抖 150 ms；连续拖动结束才真正检测。
- **`maxRadius = 0` 在 OpenCV 中表示无上限**，与「半径为 0 的圆」无关 → 在 `HoughParams.validate()` 与 README 参数表中明确该语义，避免误判为非法值。
- **OpenCV 版本差异**（apt 4.6 vs pip 4.10）可能使同一参数的检出数不同 → 测试用宽松误差（≤2 像素、数量相等）且仅针对合成实心圆，不锁定绝对数量以外的像素细节。

# Tasks

## 1. 核心参数与检测逻辑

- [x] 1.1 新建 `src/hough_gui/core/params.py`：`HoughParams` 数据类（默认 `dp=1.0, min_dist=50, param1=100, param2=30, min_radius=0, max_radius=0`）与 `validate() -> list[str]`，覆盖 `dp/min_dist/param1/param2 <= 0`、`max_radius > 0 且 min_radius > max_radius`；验证：`tests/test_params.py` 断言默认值合法、三类非法组合各返回非空错误列表
- [x] 1.2 新建 `src/hough_gui/core/detector.py`：`Circle` NamedTuple 与 `detect_circles(image, params)`（单通道跳过 `cvtColor`，`None` 归一化为 `[]`，非法参数抛 `ValueError`）；验证：`tests/test_detector.py` 用合成 640×480 图（半径 40/60/80 白圆）断言 3 个圆且圆心/半径误差 ≤ 2 像素、全黑图返回 `[]`、同一图 BGR 与灰度结果数量一致且误差 ≤ 1 像素
- [x] 1.3 新建 `src/hough_gui/__init__.py`（`__version__ = "0.1.0"`）与 `core/__init__.py`；验证：`.venv/bin/pip install -e . --no-deps` 成功，`.venv/bin/python -c "import hough_gui; print(hough_gui.__version__)"` 输出 `0.1.0`

## 2. 图片 I/O 与叠加渲染

- [x] 2.1 `src/hough_gui/core/imageio.py`：`load_image(path)` 用 `np.fromfile` + `cv2.imdecode(..., IMREAD_COLOR)`，解码失败抛 `ValueError`；验证：`tests/test_imageio.py` 在 `tmp_path` 下用中文文件名写出 PNG 再读回，断言形状与像素一致；对 `.txt` 内容断言抛 `ValueError`
- [x] 2.2 同文件 `render_overlay(image, circles)`：原分辨率副本上 `cv2.circle` 画轮廓 `(0,255,0)`、圆心 `(0,0,255)` 半径 3 px，线宽 `max(2, round(min(h,w)/300))`，零检出返回副本；验证：测试断言返回形状等于输入、零检出版本与输入逐像素相等、有圆版本在圆心处像素等于 `(0,0,255)`
- [x] 2.3 同文件 `save_annotated(path, image)`：`cv2.imencode(".png")` + `tofile`，先写 `<path>.tmp` 再 `os.replace`，失败时清理临时文件；验证：测试断言导出文件可被 `cv2.imdecode` 读回且尺寸与原图一致；对只读目录断言抛异常、既有同名文件字节不变、目录中无 `.tmp` 残留

## 3. 图形界面

- [x] 3.1 新建 `src/hough_gui/ui/main_window.py` 的 `MainWindow` 骨架与 `src/hough_gui/ui/__init__.py`：`QHBoxLayout`（左 `QFormLayout` 参数面板、右预览 `QLabel`）+ `QStatusBar` 两个标签（`图片: -`、`圆: -`）+ 「打开图片」「导出标注图」动作（导出初始禁用）；参数控件为 `QDoubleSpinBox`（dp 1.0–3.0 步长 0.1）与五个 `QSpinBox`（minDist 1–2000、param1 1–500、param2 1–200、minRadius/maxRadius 0–2000）；同组新建 `src/hough_gui/__main__.py`（`main()` 创建 `QApplication` 与 `MainWindow`）；验证：`PYTHONPATH=src python3 -m hough_gui` 能打开窗口，控件范围与默认值如上、导出按钮为灰
- [x] 3.2 实现打开流程与后台检测：`open` 调 `load_image`，失败用 `QMessageBox.critical` 并保持既有状态；`DetectThread(QThread)` 携带 `generation`、图像 `.copy()` 与参数，`run()` 内调 `detect_circles` 并 `time.perf_counter()` 计时，发 `finished_result(generation, circles, elapsed_ms)`；`MainWindow._generation` 自增后在回调中比对丢弃陈旧结果；`valueChanged` → 150 ms single-shot `QTimer` 防抖；`closeEvent` 中对运行中的线程 `wait()`；验证：手动连续快速拖动 `param2` 后最终预览对应最后值（比较状态栏数量与末次参数），关闭窗口不崩溃
- [x] 3.3 实现预览与状态栏更新：叠加图经 `QImage` → `QPixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)`，`resizeEvent` 重算；状态栏左侧 `图片: <文件名> (<宽>×<高>)`、右侧 `圆: <n> | 耗时: <ms:.1f> ms`；参数非法时参数面板下方红字显示错误、跳过检测、保留上次预览；验证：手动打开图片后缩放窗口确认图像等比且不裁剪、状态栏文本格式与 spec 一致；`minRadius=50, maxRadius=30` 时出现红字且不发起检测
- [x] 3.4 实现导出：`QFileDialog.getSaveFileName` 默认 `<原目录>/<stem>_circles.png`，用户输入无扩展名时补 `.png`，调用 `save_annotated`，异常用 `QMessageBox.critical`；验证：手动导出后 `.venv/bin/python -c "import cv2;print(cv2.imread('<导出的png>').shape)"` 得到与原图相同的 `(h, w, 3)`
- [x] 3.5 在 `pyproject.toml` 增加 `[project.scripts] hough-gui = "hough_gui.__main__:main"`；验证：`.venv/bin/pip install -e . --no-deps` 后 `.venv/bin/hough-gui` 能显示窗口，`.venv/bin/python -m hough_gui` 同样可用
- [x] 3.6 更新 `README.md`：「现状」改为已实现、「目标功能」改为实际用法与三步操作（打开 → 调参 → 导出）、参数表默认值改为 1.0/50/100/30/0/0 并标注 `maxRadius=0 表示无上限`、目录结构去掉「待首个 change 创建」标注、补充 `python3 -m hough_gui` 启动方式；验证：按 README 的安装/运行/测试命令逐条执行均成功

## 4. 集成验收

- [x] 4.1 端到端手动验收：用 `cv2` 生成 640×480 含 3 个白圆的 PNG，打开后状态栏显示 `圆: 3`，把 `param2` 从 30 调到 200 后数量下降，导出文件尺寸为 640×480 且含绿色圆轮廓
- [x] 4.2 `pytest` 全部通过，`openspec validate add-hough-circle-gui --strict` 输出 `is valid`

## Workflow follow-up

- 归档前确认 4.1/4.2 均已完成。
- 归档：`openspec archive add-hough-circle-gui`，随后复核 `openspec/specs/{image-io,circle-detection,detection-workbench}/spec.md` 已生成。

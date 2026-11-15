# Proposal

## Why

手工调 `cv2.HoughCircles` 参数目前只能反复改脚本、跑一次看一次结果，无法直观比较参数对检出效果的影响。需要一个单图交互式工具：导入图片后调整参数即时预览，并把满意的结果导出为标注图，用于算法调试与结果汇报。

## What Changes

- 新增可运行的 GUI 程序 `python3 -m hough_gui`：左侧参数面板、中央图像预览、底部状态栏。
- 新增 `hough_gui/core/imageio.py`：中文路径安全的图片读取与标注图导出（PNG）。
- 新增 `hough_gui/core/detector.py`：封装 `cv2.HoughCircles`，输入灰度图 + 参数对象，返回圆列表；不依赖 Qt。
- 新增 `hough_gui/core/params.py`：检测参数的数据结构与取值范围校验。
- 新增 `hough_gui/ui/main_window.py`：参数面板、预览控件、打开/导出动作、后台检测与陈旧结果丢弃。
- 新增 `tests/`：检测逻辑与图片读写的 pytest 用例（运行时合成图像，不提交二进制文件）。
- `pyproject.toml` 增加 `[project.scripts]` 入口 `hough-gui = "hough_gui.__main__:main"`。
- `README.md` 更新「现状」「目标功能」「使用流程」「目录结构」，去掉「尚未实现」表述。

## Capabilities

### New Capabilities
- `image-io`: 图片导入与标注图导出；要求中文路径可用、无法识别或读取失败时有可见提示、导出保持原分辨率。
- `circle-detection`: 霍夫圆检测的参数模型与结果语义；参数校验、检出圆的数据结构、零检出时的行为。
- `detection-workbench`: GUI 工作台行为；打开图片、参数变化触发重检、预览叠加、显示圆数量与耗时、参数非法时阻止重检。

### Modified Capabilities

无（当前尚无基线规格，首次归档时生成）。

## Impact

- 新增代码：`src/hough_gui/`（`__init__.py`、`__main__.py`、`core/`、`ui/`）与 `tests/`。
- 依赖：无新增，复用系统 OpenCV 4.6、PyQt5 5.15、NumPy 1.26。
- `pyproject.toml`：新增 console script 入口；`README.md`：用法与现状更新。
- 不触碰 `openspec/specs/`（基线由归档步骤生成）。

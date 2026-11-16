# 交接说明

日期：2026-11-16
变更：`add-video-detection-input`
Issue：[#1 支持导入视频并逐帧检测](https://github.com/buyuhai/camera_test/issues/1)
工作分支：`feat/1-video-import-detection`

## 当前完成

- 图片模式已实现并通过验收：导入 PNG/JPEG/BMP/TIFF、六参数调参、参数变化自动重检、后台检测、叠加预览、状态栏数量与耗时、原分辨率标注图导出。
- 两个历史变更已归档，任务全部完成：
  - `add-hough-circle-gui`：14/14
  - `add-real-image-acceptance`：8/8
- 基线规格位于 `openspec/specs/{image-io,circle-detection,detection-workbench}/spec.md`。
- 真实图片验收通过：盘子 1 个圆（圆心约 `(263.5, 256.5)`，半径约 `243.3 px`），硬币 2 个圆（半径约 `180.0/179.5 px`），证据图在 `docs/acceptance/`；输入图已随分支提交到 `docs/acceptance/inputs/`，README 的无界面复核命令可直接离线运行。
- 自动化测试：`.venv/bin/python -m pytest` 共 21 个用例通过。
- 本次视频变更只完成规划：`proposal.md`、`specs/`、`design.md`、`tasks.md` 已就绪，代码未改动。

## 环境快照

- 系统：Linux 6.18.58.1-microsoft-standard-WSL2（Ubuntu 24.04）
- Python：3.12.3
- OpenCV：4.6.0
- NumPy：1.26.4
- PyQt5 / Qt：5.15.13
- 启动：`.venv/bin/python -m hough_gui`

## 未验证事项

- 视频功能尚未实现：本变更的 11 个任务全部未开始，`openspec status --change add-video-detection-input` 显示 0/11。
- 视频解码能力未验证：MP4/AVI/MOV 的实际可用性取决于系统 OpenCV 的 FFmpeg 后端，需用样例视频逐个确认。
- `cv2.VideoCapture` 对中文路径的行为未实测；图片路径已用 `np.fromfile` 规避，视频没有等价的直接替代入口。
- 视频播放性能未验证：检测速度低于视频帧率时的跳帧表现、内存占用和界面响应都还没有实测数据。
- GUI 交互仍以手工验收为主：暂停/继续/停止、窗口缩放、导出对话框没有自动化 UI 测试。
- WSLg 标题栏由 Weston 绘制，中文标题会显示为方框，因此窗口标题固定为英文；界面字体依赖宿主 Windows 字体或 `fonts-noto-cjk`。
- 根目录 `samples/` 不入库，但同一内容的验收输入图已提交在 `docs/acceptance/inputs/`；README 的复核命令使用提交路径，不依赖本地 `samples/`。
- 仓库没有 CI，交付前需手工运行 pytest 与 `openspec validate --strict`。

## 后续待办

1. 先完成任务 1.1：确认是否需要音频、导出标注视频、进度条/逐帧单步，以及跳帧策略是否可接受；把结论补回本文件和 `design.md`。
2. 按 `tasks.md` 的第 2–5 组实现视频读取、检测线程、界面与验收；建议先做最小闭环「打开视频 → 首帧检测 → 播放/暂停/停止」，再补中文路径和末尾处理。
3. 选择一段可公开使用的短视频样例，记录来源、许可、尺寸、帧率和编码；样例本身不入库。
4. 完成后运行 `.venv/bin/python -m pytest` 和 `openspec validate add-video-detection-input --strict`，把实际输出写入 `verification.md`。
5. 评审通过后归档：`openspec archive add-video-detection-input`，确认 `openspec/specs/video-input/spec.md` 生成且 `detection-workbench` 的 MODIFIED Requirement 合入基线。

## 接手命令

```bash
git switch feat/1-video-import-detection
. .venv/bin/activate
python -m pytest
openspec status --change add-video-detection-input --json
openspec instructions apply --change add-video-detection-input --json
```

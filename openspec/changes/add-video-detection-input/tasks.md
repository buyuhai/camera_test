# Tasks

## 1. 范围确认与样例

- [ ] 1.1 与需求方确认 `design.md` 的 Open Questions：是否需要音频、导出视频、进度条/逐帧单步，以及跳帧策略是否可接受；把结论写入 `handover.md`；验证：四个问题都有明确答复，且与 `specs/video-input/spec.md` 的范围一致
- [ ] 1.2 获取一段可公开使用的短视频样例，记录来源、许可、尺寸、帧率与编码到 `README.md` 的样例获取章节；验证：按记录可重新取得样例，`samples/` 仍被 `.gitignore` 排除

## 2. 视频读取与检测核心

- [ ] 2.1 新增 `src/hough_gui/core/videoio.py`：打开视频、读取尺寸/帧率/总帧数、逐帧迭代并在结束时释放 `VideoCapture`；验证：`tests/test_videoio.py` 用 `cv2.VideoWriter` 在 `tmp_path` 生成短视频，断言总帧数与每帧尺寸正确
- [ ] 2.2 在 `videoio` 中处理无法解码文件和中文路径；验证：测试断言无法解码文件抛出带路径的错误，中文文件名可正常打开并读到至少一帧

## 3. 视频检测线程

- [ ] 3.1 在 `src/hough_gui/ui/main_window.py` 实现 `VideoDetectThread`：循环读帧、按当前参数调用 `detect_circles`、用 `render_overlay` 叠加并发出「帧序号/总数/圆列表/单帧耗时」信号；验证：用合成短视频跑完 N 帧，收到的帧序号单调递增且最终等于总帧数
- [ ] 3.2 实现播放/暂停/停止与窗口关闭时的线程退出；验证：播放中分别触发暂停、停止、关闭窗口，线程在 2 秒内结束，进程不崩溃且无残留线程

## 4. 界面与文档

- [ ] 4.1 增加「打开视频」「播放/暂停」「停止」动作和视频模式状态；打开视频后禁用「导出标注图」，图片模式保持现有行为；验证：启动、打开图片、打开视频三种状态与 `specs/detection-workbench/spec.md` 的控件场景一致
- [ ] 4.2 状态栏在视频模式显示 `帧: <当前>/<总数> | 圆: <数量> | 耗时: <毫秒> ms`；参数变化从下一帧生效；验证：播放中修改 `param2`，状态栏与叠加结果从后续帧开始变化
- [ ] 4.3 更新 `README.md` 的视频用法、样例获取与视频模式限制；验证：按 README 步骤能打开样例视频并看到逐帧检测结果

## 5. 集成验收

- [ ] 5.1 用样例视频手工验收播放、暂停、继续、停止、播放到末尾、中文路径和无法解码文件；把实际输出与结果写入 `verification.md`；验证：每个场景都有记录，且与 `specs/video-input/spec.md` 的 Scenario 对应
- [ ] 5.2 运行 `.venv/bin/python -m pytest` 与 `openspec validate add-video-detection-input --strict`；验证：pytest 全部通过，OpenSpec 输出 `is valid`

## Workflow follow-up

- 评审通过后归档：`openspec archive add-video-detection-input`。
- 归档后确认 `openspec/specs/video-input/spec.md` 已生成，`detection-workbench` 的 MODIFIED Requirement 已合入基线。
- 如果需求方要求导出标注视频或音频，另开独立变更，不在本变更中扩展范围。

# 霍夫圆检测工具

基于 OpenCV `HoughCircles` 的单图交互式调参 GUI（PyQt5）：导入图片、调节参数、预览检测结果、导出标注图。发行名 `hough-circle-gui`，导入名 `hough_gui`。

## 现状

本仓库当前**仅含脚手架**：Python 打包配置、Git 约定与 OpenSpec 工作流（`openspec/`、`.agents/skills/`）。GUI 与检测逻辑尚未实现，将由首个 OpenSpec change 落地——`src/hough_gui/`、`tests/` 到那时才出现，入口 `python3 -m hough_gui` 目前不可用。

## 环境要求

- Ubuntu 24.04 + ROS 2 Jazzy（本仓库已验证的环境）
- Python ≥ 3.10
- 系统包：`sudo apt install python3-opencv python3-pyqt5 python3-venv python3-pytest`
- WSL2 下需要 WSLg：`echo $DISPLAY` 应输出非空值（如 `:0`）

## 安装

```bash
# 1. 虚拟环境（现在即可创建）
python3 -m venv --system-site-packages .venv
. .venv/bin/activate

# 2. 可编辑安装（首个 change 创建 src/hough_gui/ 后执行；此前因 src/ 不存在会报错）
pip install -e . --no-deps
```

`--system-site-packages` 让虚拟环境复用系统已装的 `cv2` 与 `PyQt5`（与 ROS 2 rqt 同源）；`--no-deps` 阻止 pip 用 PyPI wheel 覆盖这些 apt 包。`pyproject.toml` 中声明的依赖是运行时契约，供非 ROS 环境或 CI 参考。

## 目标功能（尚未实现）

- **导入图片**：PNG / JPEG / BMP / TIFF，支持中文路径
- **调参预览**：参数变化后重跑检测，在原图上叠加圆轮廓与圆心
- **结果统计**：显示检出圆数量与检测耗时
- **导出标注图**：把叠加结果另存为 PNG

非功能约束：

- 文件读写支持中文路径：`np.fromfile` + `cv2.imdecode` / `cv2.imencode` + `tofile`，不用 `cv2.imread` / `cv2.imwrite`
- 图像一律渲染在 Qt 控件中，不使用 `cv2.imshow`
- 检测逻辑与 Qt 解耦（`hough_gui/core/`），可无界面单测

## 参数说明

初始值取 OpenCV 4.6 语义，最终以实现为准。

| 参数 | 含义 | 建议范围 | OpenCV 默认 |
|---|---|---|---|
| `dp` | 累加器分辨率与图像分辨率之比 | 1.0–2.0 | 1.0 |
| `minDist` | 圆心最小间距（像素） | 10–图像短边/4 | 必填 |
| `param1` | Canny 高阈值（低阈值取其一半） | 50–200 | 100 |
| `param2` | 圆心累加器阈值，越小检出越多 | 10–100 | 100 |
| `minRadius` | 最小半径（像素） | 0–短边/4 | 0 |
| `maxRadius` | 最大半径（像素） | 0 或 > `minRadius` | 0 |

调参直觉：`param2` 过小会误检、过大则漏检；`minDist` 小于目标圆间距时，同一个圆会被重复检出。

## 目录结构

```text
camera_test/
├── .agents/skills/                # openspec init 生成（oh-my-pi 技能，随仓库入库）
├── .gitignore
├── README.md
├── pyproject.toml
├── openspec/
│   ├── config.yaml                # schema + 项目上下文（Agent 每次读取的约束）
│   ├── specs/                     # 基线能力规格（首个 change 归档后出现）
│   └── changes/                   # 变更提案；archive/ 存已归档变更
├── src/hough_gui/                 # 待首个 change 创建
│   ├── __main__.py
│   ├── core/detector.py
│   ├── core/imageio.py
│   └── ui/main_window.py
└── tests/                         # 待首个 change 创建
```

## 开发流程（OpenSpec）

`openspec/specs/` 是归档产物，**不手工编辑**；所有功能变更都走 change 提案。

1. `/openspec-propose "<想法>"` —— 一次生成 `proposal.md`、`specs/<capability>/spec.md`（delta）、`design.md`、`tasks.md`
2. `/openspec-apply-change` —— 按 `tasks.md` 实施并逐条勾选
3. `/openspec-archive-change` —— 归档变更，把 delta 合入基线规格

其他技能：`/openspec-explore`（先想清楚）、`/openspec-update-change`（修订提案）、`/openspec-sync-specs`（不归档只同步规格）。core profile 只生成上述 6 个；`new`、`continue`、`ff`、`bulk-archive`、`verify`、`onboard` 用 `openspec config profile` 追加。

常用 CLI：

| 命令 | 用途 |
|---|---|
| `openspec list` | 列出未归档变更 |
| `openspec list --specs` | 列出基线能力 |
| `openspec show <change>` | 查看变更详情 |
| `openspec validate --strict` | 校验变更与规格格式 |
| `openspec archive <change>` | 归档变更（CLI 等价于技能） |
| `openspec context` | 打印 Agent 看到的项目上下文 |

## 测试

```bash
pytest
```

测试配置在 `pyproject.toml`（`testpaths = ["tests"]`）。用例图像由 cv2 合成（画圆），不提交二进制图片。

## Git 约定

提交信息 `<type>: <short description>`，`type` ∈ `feat | fix | refactor | docs | chore | test | build`，描述用简短英文，例如 `feat: add hough circle detector core`。当前为单分支 `main`、单开发者直接提交。

## 纳入 / 不纳入版本库

纳入：

- `pyproject.toml`、`README.md`、`.gitignore`
- `openspec/**`（`config.yaml`、`specs/`、`changes/`）
- `.agents/skills/**`（OpenSpec 生成的技能，保证 Agent 行为可复现）
- `src/**`、`tests/**`（首个 change 起出现）

不纳入：

- `.venv/`（本机虚拟环境）
- `__pycache__/`、`*.egg-info/`、`.pytest_cache/`、`build/`、`dist/`（构建与缓存产物）
- `samples/`、`out/`、`*.log`（本地测试图与导出结果）
- `.vscode/`、`.idea/`、`.DS_Store`（编辑器）

理由：可复现的配置与规格入库，环境、缓存、二进制图片不入库。

## 常见问题

- **Qt 起不来 / `xcb` 插件加载失败**：WSL2 需 WSLg，确认 `echo $DISPLAY` 非空，必要时执行 `wsl --update`。
- **中文路径读不出图**：`cv2.imread` / `cv2.imwrite` 对非 ASCII 路径不可靠，统一走 `np.fromfile` + `cv2.imdecode` 与 `cv2.imencode` + `tofile`。
- **venv 里装了 PyQt5 wheel，与 rqt 冲突**：`pip uninstall PyQt5`，用 `--system-site-packages` 重建 venv，复用系统包。

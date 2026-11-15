# Tasks

## 1. 规格确认

- [x] 1.1 在 `specs/circle-detection/spec.md` 增加「检出半径贴合目标最外沿」Requirement，以及硬币外齿圈、盘子外沿两个 Scenario；验证：`openspec validate add-real-image-acceptance --strict` 通过

## 2. 样图与验收证据

- [x] 2.1 把根目录两张样图移入 `samples/plate.png` 与 `samples/coins.jpg`，删除 `Zone.Identifier` 附属文件；验证：仓库根目录只剩工程文件，`samples/` 仍被 `.gitignore` 排除
- [x] 2.2 用各自验收参数重新检测并生成 `docs/acceptance/plate_result.png`、`docs/acceptance/coins_result.png`；验证：盘子 1 个圆、半径约 243.3 px；硬币 2 个圆、半径约 180.0/179.5 px，绿圈落在最外沿
- [x] 2.3 调整 `.gitignore` 与 `openspec/config.yaml` 的二进制图片约束，只允许 `docs/acceptance/` 下的验收证据图入库；验证：`git status --short` 中样图不出现、结果图出现

## 3. README 与验收记录

- [x] 3.1 更新 `README.md`：写明启动方式、两张图各自的验收参数表、检测结果与两张结果图，并同步目录结构和纳入/不纳入清单；验证：按 README 命令可启动，图片相对路径存在
- [x] 3.2 新增 `acceptance.md`，记录环境、输入尺寸、验收参数、实测结果、证据图与复核命令；验证：记录数值与实跑输出一致

## 4. 验收

- [x] 4.1 无界面复核两张图：盘子返回 1 个圆、硬币返回 2 个圆，半径误差不超过 2 px；验证：打印结果与 `acceptance.md` 一致
- [x] 4.2 运行 `.venv/bin/python -m pytest`，全部用例通过

## Workflow follow-up

- 归档：`openspec archive add-real-image-acceptance`；归档后确认 `openspec/changes/archive/2026-11-15-add-real-image-acceptance/` 含 `proposal.md`、`specs/`、`design.md`、`tasks.md`、`acceptance.md`，且基线 `circle-detection` 已包含外沿贴合 Requirement。

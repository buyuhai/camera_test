# Proposal

## Why

真实图片验收暴露了一个未写入基线规格的行为：带同心纹理的目标（硬币齿圈、盘子边沿）必须把半径贴到最外沿，而不是停在内部纹理上。该行为已由 `443c86e` 的梯度微调实现，但规格、验收参数与结果证据都没有留在仓库里，README 也没有明确启动方式和逐图验收参数。

## What Changes

- 在 `circle-detection` 基线规格中补充「检出半径贴合目标最外沿」的 Requirement 与硬币/盘子 Scenario，让外沿微调成为可验收的规格行为。
- 新增 `docs/acceptance/`：提交盘子与硬币两张标注结果图，作为验收证据；原始图片仍只保留在本地 `samples/`。
- 整理根目录：两张样图移入 `samples/` 并改为稳定文件名，删除 Windows `Zone.Identifier` 附属文件。
- 更新 `README.md`：写明启动方式、两张图各自的验收参数、检测结果（圆数量/半径）与结果图。
- 更新 `.gitignore` 与 `openspec/config.yaml` 的项目上下文，只对 `docs/acceptance/` 放行二进制验收图，其余测试图继续保持不入库。
- 新增本变更的 `acceptance.md`，记录规格确认、实施进度和验收结果，随变更一起归档。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `circle-detection`: 新增外沿半径贴合要求；规定带同心纹理目标在给定真实图片与参数下必须检出外沿圆，不得把内圈纹理当作最终结果。

## Impact

- 文档与仓库结构：`README.md`、`.gitignore`、`openspec/config.yaml`、`docs/acceptance/`、`samples/`。
- 规格：`openspec/specs/circle-detection/spec.md`（由归档步骤合并 delta）。
- 运行时代码：无改动；外沿微调已在 `443c86e` 实现，本次只补齐规格、验收参数与证据。
- 依赖：无新增。

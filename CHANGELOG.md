# 更新日志

本项目的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- `AGENTS.md` 发布流程新增第 6 步「同步博客」：每次发布须同步更新 Hexo 博文并部署

## [1.2.0] - 2026-08-08

### 新增
- **版本管理体系** — 新增本更新日志，Git tag 从 v1.0.0 起回溯补齐，此后每次发布打对应 tag 并附版本说明
- **依赖清单** `requirements.txt`（核心依赖：jieba + scikit-learn）与 `requirements-optional.txt`（AIGC 模型模式、学校文件读取等可选依赖，含 torch 版本陷阱说明）
- `AGENTS.md` — AI 代理协作约定：接手必读、单一计划文件原则、发布流程（更新日志 → 版本号 → tag → 推送）
- README 增加版本徽章与「版本管理」章节

### 优化
- `check_consistency.py`：数字检查新增**跨文件矛盾预警**——同组不同数字分散在不同文件（如 ch01 写 46 个、ch02 写 48 个）会标黄提示人工核对，原先只检测同一文件内的矛盾
- `check_aigc.py`：规则模式下明确打印当前检测模式，避免用户误以为模型检测已生效
- README 安装说明改为 `pip3 install -r requirements.txt`，目录结构同步补齐新文件

## [1.1.0] - 2026-08-07

### 新增
- **学校要求摄入工作流** `references/school-requirements-workflow.md` — 把学校官方文件（通知/格式规范/模板/评分标准）喂给 AI，合并生成 `school-requirements-spec.md` 硬约束规范：归档 → 按格式提取（pymupdf/textutil/python-docx/openpyxl）→ 规范骨架模板 → 使用协议 + 6 条实测坑
- `SKILL.md` 新增第十二章「学校要求摄入」，README 增加「第 0 步」入口

## [1.0.0] - 2026-08-06

### 新增
- **首次发布**：从一次完整毕业论文 AI 制作周期（选题→初稿→降重→AIGC清理→排版→提交）提炼的全流程方法论
- `SKILL.md` — 可作为 Claude Code Skill 安装：写作顺序策略（先实现后理论）、查重降重（结构性重复对照表/高危句式/降重红线）、AIGC 降 AI 率、跨章一致性审计（代码是唯一事实来源）、MD→Word 工作流、图表与参考文献要求、多 AI 协作防回退、28 条实战坑清单
- `scripts/check_plagiarism.py` — 内部查重（jieba 分词 + TF-IDF + 余弦相似度），含超长段落检测与逐章字数统计
- `scripts/check_aigc.py` — AIGC 检测双模式：`Hello-SimpleAI/chatgpt-detector-roberta-chinese` 模型模式 + 规则模式自动降级
- `scripts/check_consistency.py` — 互斥术语组 / 互斥数字组跨章一致性检查
- MIT License

[1.2.0]: https://github.com/luodeCoding/ai-thesis-writing/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/luodeCoding/ai-thesis-writing/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/luodeCoding/ai-thesis-writing/releases/tag/v1.0.0

# AGENTS.md — AI 代理协作约定

本仓库是「AI 毕业论文写作工具箱」：方法论（SKILL.md）+ 检测脚本（scripts/）+ 学校要求摄入流程（references/）。

## 接手必读

1. 先读 `README.md` 了解仓库全貌，再读 `CHANGELOG.md` 尾部确认当前版本与最近变更
2. 对任何"与上次不一致"的内容，先查文件/git 历史确认，不要凭上一次会话的记忆改
3. 脚本修改后必须 `python3 -m py_compile scripts/*.py` 验证

## 修改原则

- `SKILL.md` 是方法论主体，开头必须有合法的 skill frontmatter（name + description）
- 脚本保持**单文件自包含、参数化设计**，不绑定具体论文项目，不引入必须安装的重依赖（torch/transformers 等保持可选降级）
- README 与 SKILL.md 内容联动：新增章节/脚本时两边同步

## 发布流程（版本管理）

每次发布必须按顺序完成以下步骤，缺一不可：

1. **更新 `CHANGELOG.md`** — 按 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式新增版本段（新增/优化/修复分类），并更新底部的版本对比链接
2. **更新版本号** — README 顶部的版本徽章 + 「版本管理」章节的当前版本号
3. **提交** — commit message 格式：`类型: 描述`（feat/fix/docs/chore/release）
4. **打 tag** — `git tag -a vX.Y.Z -m "版本说明"`，tag 与 CHANGELOG 版本段一一对应
5. **推送** — `git push origin main --tags`，并用 `gh release create vX.Y.Z --notes "..."` 创建 GitHub Release
6. **同步博客** — 更新博文 `~/Desktop/博客/HexoRoder/source/_posts/AI毕业论文踩坑实录.md`（在「🆕 更新记录」章节追加本次版本内容），然后 `npx hexo generate && npx hexo deploy` 部署，并把博文源码提交推送到 hexo 分支

版本号规则（语义化版本）：新增方法论章节/脚本 → MINOR；文案修订/小优化 → PATCH；结构重构 → MAJOR。

# AI 毕业论文写作工具箱（ai-thesis-writing）

> 用 AI 辅助完成毕业论文的全流程经验提炼 + 配套检测脚本。
> 从一次完整的论文制作周期（选题→初稿→降重→AIGC清理→排版→提交）中总结的 28 个实战坑。

## 这个仓库是什么

用 AI 写毕业论文，最大的风险不是"写不出来"，而是：

- **查重率过高**：AI 生成的技术介绍与网络资料高度雷同
- **AIGC 检测不过**：学校开始用 AI 检测工具筛查
- **自我重复拉高查重率**：绪论/结论/各章小结天然互相重复
- **多轮编辑后数据打架**：不同章节的数字、术语互相矛盾
- **排版返工**：格式问题拖到最后一刻才发现

本仓库提供一套经过实战验证的完整方法论（SKILL.md）+ 3 个可直接运行的检测脚本。

## 快速开始

```bash
git clone https://github.com/luodeCoding/ai-thesis-writing.git
cd ai-thesis-writing
pip3 install jieba scikit-learn
```

### 1. 内部查重（花钱查重前必做）

```bash
python3 scripts/check_plagiarism.py ~/my-thesis --glob "chapters/*.md"
```

基于 jieba 分词 + TF-IDF 向量化 + 余弦相似度，检测章节之间的内部重复段落、超长段落（可能是 AI 一口气生成的），并输出逐章字数统计。

### 2. AIGC 检测

```bash
python3 scripts/check_aigc.py ~/my-thesis --glob "chapters/*.md"
```

双模式：
- **模型模式**：`Hello-SimpleAI/chatgpt-detector-roberta-chinese`（需 torch≥2.4）
- **规则模式**（模型不可用时自动降级）：AI 写作特征关键词评分

```bash
# 强制规则模式（无需 torch）
python3 scripts/check_aigc.py ~/my-thesis --glob "*.md" --rules-only
```

### 3. 一致性检查（降重改写后必做）

```bash
python3 scripts/check_consistency.py ~/my-thesis --glob "*.md" \
  --terms "三级检索,双通道;管理端,后台系统" \
  --numbers "13项,17项;46个,48个"
```

- `--terms`：互斥术语组——同一组术语在全文出现多种说法 = 术语漂移
- `--numbers`：互斥数字组——同一文件出现同组多个数字 = 数据矛盾

## 核心方法论（详见 SKILL.md）

### 写作顺序：先实现后理论

```
第5章 系统实现（代码现成，最安全）   ← 第一个写
第4章 系统设计
第1章 绪论
第3章 需求分析
第6章 系统测试（跑真实系统获取数据）
第7章 总结与展望
第2章 相关技术（查重风险最高）       ← 最后写
摘要 + 关键词
```

### 降重核心策略

| 问题 | 解法 |
|------|------|
| 设计章和实现章贴相同代码 → 相似度100% | 设计章改方法签名表格，实现章保留代码 |
| 绪论↔结论 重复 55-70% | 绪论用"将要做什么"，结论用"做到了什么"+量化 |
| 测试章总结↔结论 重复 60-65% | 分析段改引用式（"如表6-11所示"） |
| 高危句式（"XX是基于YY的ZZ"） | 加出处、换句式、加细节、换主语 |

### 一致性审计：代码是唯一事实来源

论文描述必须与代码一致，而非反过来。不确定的数据必须去代码里验证（`grep add_node | wc -l`、`wc -l`），不能凭记忆改。答辩 PPT、开题报告、摘要等衍生文件同样引用关键数字，grep 时不能只扫正文章节。

### MD → Word 工作流

MD 是源文件，Word 是生成物。用 python-docx 脚本生成，不经过 HTML。注意四个已知坑：表格标题重复、附录编号归零、致谢不进目录（必须用 Heading 1 style）、目录域需手动更新。

## 28 条实战坑清单

完整列表见 [SKILL.md](SKILL.md) 第十二章，精选最高频的 10 条：

1. 第2章（相关技术）最容易翻车，必须用自己的话重写
2. 测试数据不能编，跑真实系统记录
3. 花钱查重前先自查内部重复（内部重复往往是查重率主要来源）
4. 降重时术语漂移——引入新术语导致全文不一致
5. 降重时数字出错——凭记忆写数字，必须核实源表格
6. 跨章引用不同步——改了一章的数字，其他章要同步
7. 绪论"研究内容"和"组织结构"天然撞车，用不同切入点写
8. 摘要关键词用"；"分隔，不是"、"
9. 文献综述不能只罗列，必须有对比分析和选型理由
10. 多 AI 模型轮流编辑会互相回退——接手先读 PLAN.md/CHANGELOG.md

## 适用场景

- 中国高校本科/自考毕业论文
- 计算机类"系统设计与实现"方向论文（效果最佳）
- AI 辅助写作的全流程质量控制

## 目录结构

```
├── SKILL.md                    # 完整方法论（可作为 Claude Code Skill 安装）
├── README.md
└── scripts/
    ├── check_plagiarism.py     # 内部查重（jieba + TF-IDF）
    ├── check_aigc.py           # AIGC 检测（模型+规则双模式）
    └── check_consistency.py    # 术语/数字一致性检查
```

## 作为 Claude Code Skill 使用

```bash
git clone https://github.com/luodeCoding/ai-thesis-writing.git ~/.claude/skills/ai-thesis-writing
```

然后在论文项目中对 AI 说"帮我检查论文查重风险"或"按论文写作流程继续"。

## License

MIT

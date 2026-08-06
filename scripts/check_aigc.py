#!/usr/bin/env python3
"""
AIGC 检测脚本 - 检测论文章节是否为 AI 生成
双模式：
  1. 模型模式: Hello-SimpleAI/chatgpt-detector-roberta-chinese（需 transformers + torch）
  2. 规则模式: 模型不可用时自动降级，基于 AI 写作特征评分

用法:
    python3 check_aigc.py <论文目录> [--glob "chapters/*.md"] [--rules-only]

示例:
    python3 check_aigc.py ~/my-thesis --glob "chapters/*.md"
    python3 check_aigc.py . --glob "*.md" --rules-only
"""

import argparse
import glob
import os
import re
import sys

# AI 常见写作模式关键词（规则检测用）
AI_KEYWORDS = [
    '首先', '其次', '最后', '综上所述', '总之',
    '值得注意的是', '在此基础上', '从而', '进而',
    '不仅', '而且', '同时', '此外', '因此',
    '通过.*实现了', '有效地', '显著地',
    '为.*提供了.*支撑', '具有重要意义',
]


def load_chapters(thesis_dir, file_glob):
    """读取所有匹配的 Markdown 文件，返回 {文件名: [段落列表]}"""
    pattern = os.path.join(thesis_dir, file_glob)
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"未找到匹配文件: {pattern}", file=sys.stderr)
        sys.exit(1)

    chapters = {}
    for path in files:
        fname = os.path.basename(path)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        text = re.sub(r'#+\s+.*', '', text)
        text = re.sub(r'\|.*\|', '', text)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        paragraphs = []
        for p in text.split('\n'):
            p = p.strip()
            if len(p) > 50:  # 只检测 50 字以上的段落
                paragraphs.append(p)
        chapters[fname] = paragraphs
    return chapters


def load_model():
    """尝试加载 AI 检测模型，失败返回 None"""
    try:
        print("\n⏳ 正在加载AI检测模型 (首次运行需下载约500MB)...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        model_name = "Hello-SimpleAI/chatgpt-detector-roberta-chinese"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.eval()
        print("✅ 模型加载成功\n")
        return tokenizer, model
    except Exception as e:
        print(f"⚠️ 模型加载失败: {e}")
        print("将使用基于规则的简易检测\n")
        return None


def predict_with_model(tokenizer, model, para):
    """用模型预测单段 AI 概率"""
    import torch
    inputs = tokenizer(para[:512], return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        return probs[0][1].item()  # label 1 = AI


def predict_with_rules(para):
    """规则评分：统计 AI 关键词密度，归一化为概率"""
    ai_signals = 0
    for kw in AI_KEYWORDS:
        if re.search(kw, para):
            ai_signals += 1
    ai_ratio = ai_signals / max(len(para) / 100, 1)
    return min(ai_ratio / 3, 0.95)


def main():
    parser = argparse.ArgumentParser(description='AIGC检测（模型+规则双模式）')
    parser.add_argument('thesis_dir', help='论文项目根目录')
    parser.add_argument('--glob', default='chapters/*.md',
                        help='章节文件匹配模式（默认 chapters/*.md）')
    parser.add_argument('--rules-only', action='store_true',
                        help='强制使用规则模式（跳过模型）')
    args = parser.parse_args()

    print("=" * 70)
    print("  AIGC检测 (AI生成内容检测)")
    print("=" * 70)

    model_pack = None
    if not args.rules_only:
        model_pack = load_model()

    chapters = load_chapters(args.thesis_dir, args.glob)
    total_paras = sum(len(v) for v in chapters.values())
    print(f"📂 待检测章节: {len(chapters)} 个, 共 {total_paras} 段落\n")

    all_results = []
    ai_count = 0
    human_count = 0

    for fname, paras in chapters.items():
        print(f"--- {fname} ({len(paras)} 段落) ---")
        for i, para in enumerate(paras):
            if model_pack:
                ai_prob = predict_with_model(model_pack[0], model_pack[1], para)
            else:
                ai_prob = predict_with_rules(para)

            if ai_prob > 0.5:
                ai_count += 1
                label = "AI"
                print(f"  ⚠️ [{i+1}] AI={ai_prob:.1%}: {para[:60]}...")
            else:
                human_count += 1
                label = "人写"
                if ai_prob > 0.3:
                    print(f"  🟡 [{i+1}] AI={ai_prob:.1%}(边界): {para[:60]}...")

            all_results.append({
                'file': fname,
                'para_idx': i + 1,
                'ai_prob': ai_prob,
                'label': label,
                'text': para[:200],
            })

    # 汇总报告
    print(f"\n{'='*70}")
    print("📊 AIGC检测汇总报告")
    print("=" * 70)

    total = ai_count + human_count
    if total == 0:
        print("没有可检测的段落")
        return
    print(f"\n  总检测段落: {total}")
    print(f"  人写判定: {human_count} ({human_count/total:.1%})")
    print(f"  AI判定: {ai_count} ({ai_count/total:.1%})")

    # 按章节统计
    print(f"\n  {'章节':<25} {'段落数':>6} {'AI判定':>6} {'AI比例':>8}")
    print("  " + "-" * 50)
    for fname in chapters:
        file_results = [r for r in all_results if r['file'] == fname]
        if file_results:
            file_ai = len([r for r in file_results if r['label'] == 'AI'])
            file_total = len(file_results)
            ratio = file_ai / file_total if file_total else 0
            marker = " ⚠️" if ratio > 0.3 else ""
            print(f"  {fname:<25} {file_total:>6} {file_ai:>6} {ratio:>7.1%}{marker}")

    # 高风险段落
    high_risk = [r for r in all_results if r['ai_prob'] > 0.7]
    if high_risk:
        print(f"\n{'='*70}")
        print(f"🔴 高AI风险段落 (AI概率 > 70%): {len(high_risk)} 段")
        print("=" * 70)
        for r in high_risk[:15]:
            print(f"\n  [{r['file']} 第{r['para_idx']}段] AI={r['ai_prob']:.1%}")
            print(f"  {r['text'][:150]}...")

    # 中等风险
    medium_risk = [r for r in all_results if 0.4 < r['ai_prob'] <= 0.7]
    if medium_risk:
        print(f"\n{'='*70}")
        print(f"🟡 中等AI风险段落 (40-70%): {len(medium_risk)} 段")
        print("=" * 70)
        for r in medium_risk[:10]:
            print(f"  [{r['file']} 第{r['para_idx']}段] AI={r['ai_prob']:.1%}: {r['text'][:80]}...")


if __name__ == '__main__':
    main()

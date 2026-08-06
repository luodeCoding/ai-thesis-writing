#!/usr/bin/env python3
"""
论文内部查重脚本 - 基于 jieba + TF-IDF + cosine similarity
检测论文各章节 Markdown 文件之间的内部重复段落

用法:
    python3 check_plagiarism.py <论文目录> [--glob "chapters/*.md"] [--threshold 0.3]

示例:
    python3 check_plagiarism.py ~/my-thesis --glob "chapters/*.md"
    python3 check_plagiarism.py . --glob "*.md" --threshold 0.4
"""

import argparse
import glob
import os
import re
import sys

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
        # 去掉 markdown 标记
        text = re.sub(r'#+\s+.*', '', text)          # 标题行
        text = re.sub(r'\|.*\|', '', text)            # 表格行
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)   # 图片
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # 代码块
        paragraphs = []
        for p in text.split('\n'):
            p = p.strip()
            if len(p) > 30:  # 只保留有意义的段落
                paragraphs.append(p)
        chapters[fname] = paragraphs
    return chapters


def check_internal_repetition(chapters, threshold=0.3):
    """检测论文内部段落之间的重复"""
    import jieba
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    all_paragraphs = []
    sources = []
    for fname, paras in chapters.items():
        for i, p in enumerate(paras):
            all_paragraphs.append(p)
            sources.append(f"{fname}:{i+1}")

    if len(all_paragraphs) < 2:
        return []

    def seg(text):
        return ' '.join(jieba.cut(text))

    segmented = [seg(p) for p in all_paragraphs]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(segmented)
    sim_matrix = cosine_similarity(tfidf_matrix)

    results = []
    n = len(all_paragraphs)
    for i in range(n):
        for j in range(i + 1, n):
            sim = sim_matrix[i][j]
            if sim > threshold:
                results.append({
                    'similarity': sim,
                    'para1': all_paragraphs[i][:100],
                    'para2': all_paragraphs[j][:100],
                    'source1': sources[i],
                    'source2': sources[j],
                })
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results


def check_paragraph_length(chapters, max_len=500):
    """检查过长段落（可能是 AI 一口气生成的）"""
    long_paras = []
    for fname, paras in chapters.items():
        for i, p in enumerate(paras):
            if len(p) > max_len:
                long_paras.append({
                    'file': fname,
                    'line': i + 1,
                    'length': len(p),
                    'preview': p[:100] + '...',
                })
    return long_paras


def main():
    parser = argparse.ArgumentParser(description='论文内部查重（jieba + TF-IDF）')
    parser.add_argument('thesis_dir', help='论文项目根目录')
    parser.add_argument('--glob', default='chapters/*.md',
                        help='章节文件匹配模式（默认 chapters/*.md）')
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='相似度阈值（默认 0.3）')
    args = parser.parse_args()

    try:
        import jieba
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        print("请先安装依赖: pip3 install jieba scikit-learn", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("  论文自查重报告 (jieba + TF-IDF + cosine similarity)")
    print("=" * 70)

    chapters = load_chapters(args.thesis_dir, args.glob)
    total_paras = sum(len(v) for v in chapters.values())
    print(f"\n📂 加载章节: {len(chapters)} 个")
    print(f"📝 总段落数: {total_paras}")
    for fname, paras in chapters.items():
        print(f"   {fname}: {len(paras)} 段落, {sum(len(p) for p in paras)} 字")

    # 1. 内部重复检测
    print(f"\n{'='*70}")
    print(f"📊 一、内部段落重复检测 (阈值: 相似度 > {args.threshold:.0%})")
    print("=" * 70)
    internal = check_internal_repetition(chapters, args.threshold)
    if internal:
        print(f"\n发现 {len(internal)} 对高相似度段落:\n")
        for i, r in enumerate(internal[:20]):
            print(f"  [{i+1}] 相似度: {r['similarity']:.1%}")
            print(f"      段落A ({r['source1']}): {r['para1']}")
            print(f"      段落B ({r['source2']}): {r['para2']}")
            print()
    else:
        print("✅ 未发现明显内部重复")

    # 2. 超长段落
    print(f"\n{'='*70}")
    print("📊 二、超长段落检测 (> 500字)")
    print("=" * 70)
    long_paras = check_paragraph_length(chapters)
    if long_paras:
        print(f"\n发现 {len(long_paras)} 个超长段落:\n")
        for p in long_paras:
            print(f"  [{p['file']} 第{p['line']}段] {p['length']}字")
            print(f"    {p['preview']}")
            print()
    else:
        print("✅ 所有段落长度合理")

    # 3. 逐章统计
    print(f"\n{'='*70}")
    print("📊 三、逐章统计")
    print("=" * 70)
    print(f"\n{'章节':<25} {'段落数':>6} {'总字数':>8} {'平均段长':>8}")
    print("-" * 50)
    total_words = 0
    for fname, paras in chapters.items():
        words = sum(len(p) for p in paras)
        avg = words / len(paras) if paras else 0
        total_words += words
        print(f"{fname:<25} {len(paras):>6} {words:>8} {avg:>8.0f}")
    print("-" * 50)
    print(f"{'合计':<25} {total_paras:>6} {total_words:>8}")

    # 汇总
    print(f"\n{'='*70}")
    print("📋 汇总")
    print("=" * 70)
    high_sim_count = len([r for r in internal if r['similarity'] > 0.5])
    print(f"  高相似度段落对 (>50%): {high_sim_count}")
    print(f"  中等相似度段落对 ({args.threshold:.0%}-50%): {len(internal) - high_sim_count}")
    print(f"  超长段落数: {len(long_paras)}")
    print(f"  总字数: {total_words}")


if __name__ == '__main__':
    main()

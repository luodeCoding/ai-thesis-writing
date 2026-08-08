#!/usr/bin/env python3
"""
论文一致性检查脚本 - 检测跨章节的术语漂移与数字矛盾
降重改写后最容易引入的两类问题：
  1. 术语不一致（同一概念在不同章节用了不同说法）
  2. 数字不一致（测试用例数、模块数等在不同文件对不上）

用法:
    python3 check_consistency.py <论文目录> --glob "chapters/*.md"

    术语对: 用 --terms 传入互斥术语组（逗号分隔，组间用分号分隔）
    python3 check_consistency.py . --terms "三级检索,双通道;管理端,后台系统"
    含义: "三级检索" 和 "双通道" 只能出现一种；"管理端" 和 "后台系统" 只能出现一种

    数字模式: 用 --numbers 传入需要全文统一的数字表达（逗号分隔）
    python3 check_consistency.py . --numbers "46个,48个;13项,17项"
    含义: 同一文件出现同组多个数字 = 明确矛盾；同组数字分散在不同文件 = 跨章矛盾风险（警告）
"""

import argparse
import glob
import os
import re
import sys


def load_files(thesis_dir, file_glob):
    pattern = os.path.join(thesis_dir, file_glob)
    files = sorted(glob.glob(pattern))
    if not files:
        print(f"未找到匹配文件: {pattern}", file=sys.stderr)
        sys.exit(1)
    return {os.path.basename(p): open(p, encoding='utf-8').read() for p in files}


def check_terms(files, term_groups):
    """互斥术语组检查：同一组内出现多个术语 = 术语漂移"""
    problems = []
    for group in term_groups:
        terms = [t.strip() for t in group.split(',') if t.strip()]
        hits = {}
        for fname, text in files.items():
            found = [t for t in terms if t in text]
            if found:
                hits[fname] = found
        distinct = set(t for ts in hits.values() for t in ts)
        if len(distinct) > 1:
            problems.append((group, hits))
    return problems


def check_numbers(files, number_groups):
    """互斥数字组检查：
    1. 同一文件出现同组多个数字 = 明确矛盾（problems）
    2. 同组不同数字分散在不同文件 = 跨章矛盾风险（warnings）
    """
    problems = []
    warnings = []
    for group in number_groups:
        nums = [n.strip() for n in group.split(',') if n.strip()]
        hits = {}
        for fname, text in files.items():
            found = [n for n in nums if n in text]
            if found:
                hits[fname] = found
                if len(found) > 1:
                    problems.append((fname, group, found))
        distinct = set(n for ns in hits.values() for n in ns)
        if len(distinct) > 1:
            warnings.append((group, hits))
    return problems, warnings


def main():
    parser = argparse.ArgumentParser(description='论文一致性检查（术语+数字）')
    parser.add_argument('thesis_dir', help='论文项目根目录')
    parser.add_argument('--glob', default='chapters/*.md',
                        help='文件匹配模式（默认 chapters/*.md；建议用 *.md 全项目扫描）')
    parser.add_argument('--terms', default='',
                        help='互斥术语组，组内逗号分隔，组间分号分隔')
    parser.add_argument('--numbers', default='',
                        help='互斥数字组，组内逗号分隔，组间分号分隔')
    args = parser.parse_args()

    files = load_files(args.thesis_dir, args.glob)
    print("=" * 70)
    print("  论文一致性检查报告")
    print("=" * 70)
    print(f"\n📂 扫描文件: {len(files)} 个")
    for fname, text in files.items():
        print(f"   {fname}: {len(text)} 字")

    ok = True

    if args.terms:
        print(f"\n{'='*70}")
        print("📊 一、术语一致性检查")
        print("=" * 70)
        term_groups = [g for g in args.terms.split(';') if g.strip()]
        problems = check_terms(files, term_groups)
        if problems:
            ok = False
            for group, hits in problems:
                print(f"\n  🔴 术语组 [{group}] 出现漂移:")
                for fname, found in hits.items():
                    print(f"      {fname}: 使用了 {found}")
            print("\n  修复: 全文统一为一种说法，grep 定位后逐一替换")
        else:
            print("✅ 术语组内部无冲突")

    if args.numbers:
        print(f"\n{'='*70}")
        print("📊 二、数字一致性检查")
        print("=" * 70)
        number_groups = [g for g in args.numbers.split(';') if g.strip()]
        problems, warnings = check_numbers(files, number_groups)
        if problems:
            ok = False
            for fname, group, found in problems:
                print(f"  🔴 {fname}: 数字组 [{group}] 同时出现 {found}")
            print("\n  修复: 以源表格/代码统计为准，统一所有引用处")
        if warnings:
            print("\n  ⚠️ 跨文件矛盾风险（同组不同数字分散在不同文件，需人工核对哪个为准）:")
            for group, hits in warnings:
                if any(g == group for _, g, _ in problems):
                    continue  # 已作为明确矛盾报告过
                print(f"\n  🟡 数字组 [{group}]:")
                for fname, found in hits.items():
                    print(f"      {fname}: {found}")
        if not problems and not warnings:
            print("✅ 数字组无矛盾")

    if not args.terms and not args.numbers:
        print("\n未指定检查项。用法示例:")
        print('  python3 check_consistency.py . --terms "三级检索,双通道"')
        print('  python3 check_consistency.py . --numbers "13项,17项"')

    print(f"\n{'='*70}")
    print("📋 结论: " + ("❌ 存在一致性问题，需修复" if not ok else "✅ 一致性检查通过"))
    print("=" * 70)
    sys.exit(1 if not ok else 0)


if __name__ == '__main__':
    main()

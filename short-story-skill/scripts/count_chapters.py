#!/usr/bin/env python3
"""Count a short-story manuscript: per-chapter length, dialogue ratio,
and the cutoff-anchor share.

Input is the cumulative manuscript: intro, then chapters. Each chapter
marker sits on its own line, numbered from 1 in order:
  1 / 1. / 1、 / # 1 / 第1章 / 第一章 / 第1章 重逢
A first line starting with '# ' that is not a marker is a title and is skipped.
Counts include punctuation and exclude marker lines and whitespace.

Usage:
  python3 count_chapters.py 全文.txt [--batch-from N] [--anchor-chapter N --final]
"""
import argparse
import re
import sys
from pathlib import Path

CHAPTER_MIN, CHAPTER_MAX = 500, 1000
INTRO_MIN, INTRO_MAX = 60, 200
DIALOGUE_MIN = 0.15
INTERJECTIONS = {"嗯", "啊", "哦", "哎", "呃", "哈", "咦"}

MARKERS = [
    re.compile(r"^#\s*(\d+)(?:\s+.*)?$"),
    re.compile(r"^第\s*(\d+)\s*章.*$"),
    re.compile(r"^(\d+)[\.、](?:\s+.*)?$"),
    re.compile(r"^(\d+)\s*$"),
]
CN_MARKER = re.compile(r"^第\s*([一二三四五六七八九十]+)\s*章.*$")
SUSPECTED = re.compile(r"^第.*章|^#\s*\d+|^\d+[\.、]")
CN_DIGIT = {c: i for i, c in enumerate("一二三四五六七八九", start=1)}


def cn_to_int(s):
    """Chinese numeral up to 99: 一, 十, 十一, 二十一."""
    if "十" not in s:
        return CN_DIGIT.get(s)
    a, _, b = s.partition("十")
    if (a and a not in CN_DIGIT) or (b and b not in CN_DIGIT):
        return None
    return CN_DIGIT.get(a, 1) * 10 + CN_DIGIT.get(b, 0)


def parse_marker(line):
    s = line.strip()
    for pat in MARKERS:
        m = pat.match(s)
        if m:
            return int(m.group(1))
    m = CN_MARKER.match(s)
    return cn_to_int(m.group(1)) if m else None


def clean(text):
    return re.sub(r"\s+", "", text)


def dialogue_chars(text):
    # A single quoted character is emphasis, not dialogue, unless it is an interjection.
    total = 0
    for m in re.finditer(r'[“"]([^”"]+)[”"]', text):
        seg = clean(m.group(1))
        if len(seg) >= 2 or seg in INTERJECTIONS:
            total += len(seg)
    return total


def flag(n, lo, hi):
    return "低于范围-警告" if n < lo else "超范围" if n > hi else "在范围内"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--batch-from", type=int, help="本批首章，输出本批对话占比")
    ap.add_argument("--anchor-chapter", type=int, help="锚点章号")
    ap.add_argument("--final", action="store_true", help="全篇写完后计算截断点占比")
    args = ap.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8")
    lines = raw.splitlines()
    if lines and lines[0].strip().startswith("# ") and parse_marker(lines[0]) is None:
        lines = lines[1:]

    sections, label, buf, expected, warnings = [], "引言", [], 1, []
    for lineno, line in enumerate(lines, start=1):
        num = parse_marker(line)
        if num == expected or (num is not None and num > expected > 1):
            if num != expected:
                warnings.append(
                    f"第 {lineno} 行“{line.strip()}”跳号（期望第 {expected} 章），已按第 {num} 章对齐"
                )
            sections.append((label, "\n".join(buf)))
            label, buf, expected = str(num), [], num + 1
            continue
        if num is not None or SUSPECTED.match(line.strip()):
            warnings.append(f"第 {lineno} 行“{line.strip()}”没有识别为第 {expected} 章，按正文计数")
        buf.append(line)
    sections.append((label, "\n".join(buf)))
    sections = [(l, t) for l, t in sections if clean(t)]

    if not any(l != "引言" for l, _ in sections):
        print("错误：没有识别到章节号（第 1 章起，每个章节号单独一行）。", file=sys.stderr)
        return 2

    rows = []  # (label, chars, dialogue chars)
    print(f"{'章节':>6} {'字数':>6} {'对话字数':>8} {'对话占比':>8}  范围")
    for label, text in sections:
        total, dlg = len(clean(text)), dialogue_chars(text)
        rows.append((label, total, dlg))
        rng = flag(total, INTRO_MIN, INTRO_MAX) if label == "引言" else flag(total, CHAPTER_MIN, CHAPTER_MAX)
        print(f"{label:>6} {total:>6} {dlg:>8} {dlg / total:>7.0%}  {rng}")
    for w in warnings:
        print(f"警告：{w}")
    if '"' in raw:
        print("警告：检测到直引号，正式稿请改成弯引号 “”。")

    chapters = [r for r in rows if r[0] != "引言"]
    counts = [r[1] for r in chapters]
    below = sum(c < CHAPTER_MIN for c in counts)
    above = sum(c > CHAPTER_MAX for c in counts)
    print(f"\n正文合计: {sum(counts)} 字, 章数: {len(counts)}, 平均每章: {sum(counts) / len(counts):.1f} 字, "
          f"低于范围（警告）章数: {below}, 超范围章数: {above}")
    dlg_total = sum(r[2] for r in chapters)
    print(f"累计正文对话合计: {dlg_total} 字, 累计对话占比: {dlg_total / sum(counts):.1%}")
    if args.batch_from is not None:
        batch = [r for r in chapters if int(r[0]) >= args.batch_from]
        b_total, b_dlg = sum(r[1] for r in batch), sum(r[2] for r in batch)
        b_ratio = b_dlg / b_total if b_total else 0
        print(f"本批对话合计: {b_dlg} 字, 本批对话占比: {b_ratio:.1%}")
        if b_ratio < DIALOGUE_MIN:
            print("警告：本批对话占比低于 15%。")
    total_all = sum(r[1] for r in rows)
    print(f"全文合计（含引言）: {total_all} 字")

    if args.anchor_chapter is not None:
        labels = [r[0] for r in rows]
        if not args.final:
            print("\n截断点占比只在全篇写完后计算，请加 --final。")
        elif str(args.anchor_chapter) not in labels:
            print(f"\n截断点：没有找到第 {args.anchor_chapter} 章。")
        else:
            upto = sum(r[1] for r in rows[: labels.index(str(args.anchor_chapter)) + 1])
            share = upto / total_all
            status = "在 35%-55% 内" if 0.35 <= share <= 0.55 else "不在 35%-55% 内"
            print(f"\n截断点：引言到第 {args.anchor_chapter} 章共 {upto} 字，占全文 {share:.1%}，{status}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

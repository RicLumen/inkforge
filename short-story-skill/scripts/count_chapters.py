#!/usr/bin/env python3
"""Count a short-story manuscript.

Input format (strict, fail loudly on mismatch):
  - Optional title: a first line starting with '# ' is excluded from counts.
    Do NOT put a bare title on the first line; it will be counted as intro.
  - Intro: text before the first chapter marker, no title.
  - Chapter markers, one per line, in increasing order starting at 1:
      1
      第1章 / 第一章
      第 1 章
      1.
      1、
      # 1
    Anything else is body text, not a marker. In particular, a line like
    "3 / 2 / 1" is NOT a marker, and a bare "3" that is not the next
    expected chapter number is treated as body text with a warning,
    not silently as a new chapter.

Counting: Chinese characters and punctuation, excluding chapter-marker
lines and blank lines / whitespace. Dialogue = characters inside “ ”.

Usage:
  python3 count_chapters.py <file.txt|file.md> [--anchor-chapter N]
    --anchor-chapter N: the cutoff-anchor chapter. If that chapter is in
      the file, print its cumulative words up to and including it as a
      share of the full text, and flag whether it is in 35%-55%.
      If it is not in the file yet, print "截断点尚未出现" instead of
      inventing a share. During drafting, the anchor is defined by plot
      (irreversible choice / core truth revealed / conflict escalation
      to a point of no return), not by guessing a final total; the
      script only checks the share once the draft (or the anchor
      chapter) exists. There is no estimated-total parameter, because
      a final total that is not decided yet cannot be estimated by
      the script.

Exit codes: 0 = counted, at least one chapter found; 2 = usage error
or no chapter marker found (do NOT trust an intro-only count).
Out-of-range chapters are flagged in the output; the script does not
silently pass them.
"""
import argparse
import re
import sys
from pathlib import Path

CHAPTER_MIN = 500
CHAPTER_MAX = 1000
INTRO_MIN = 60
INTRO_MAX = 200

MARKERS = [
    re.compile(r"^#\s*(\d+)\s*$"),
    re.compile(r"^第\s*(\d+)\s*章\s*$"),
    re.compile(r"^(\d+)[\.、]\s*$"),
    re.compile(r"^(\d+)\s*$"),
]

_CN_DIGIT = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
             "六": 6, "七": 7, "八": 8, "九": 9}


def cn_to_int(s: str):
    """Chinese numeral up to 99, e.g. 一, 十, 十一, 二十, 二十一."""
    if not s or any(c not in "一二三四五六七八九十" for c in s):
        return None
    if "十" not in s:
        return _CN_DIGIT[s] if len(s) == 1 else None
    a, _, b = s.partition("十")
    tens = _CN_DIGIT[a] if a else 1
    ones = _CN_DIGIT[b] if b else 0
    return tens * 10 + ones


def parse_marker(line: str):
    s = line.strip()
    for pat in MARKERS:
        m = pat.match(s)
        if m:
            return int(m.group(1))
    m = re.match(r"^第\s*([一二三四五六七八九十]+)\s*章\s*$", s)
    if m:
        return cn_to_int(m.group(1))
    return None


def clean(text: str) -> str:
    return re.sub(r"\s+", "", text)


def dialogue_chars(text: str) -> int:
    parts = re.findall(r"“([^”]*)”", text)
    return sum(len(clean(p)) for p in parts)


def flag(count: int, lo: int, hi: int) -> str:
    if count < lo:
        return "低于范围"
    if count > hi:
        return "超范围"
    return "在范围内"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--anchor-chapter", type=int, default=None)
    args = ap.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8")
    lines = raw.splitlines()
    if lines and lines[0].strip().startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]

    sections = []
    current_label = "引言"
    buf: list[str] = []
    expected = 1
    warnings: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        num = parse_marker(line)
        if num is not None:
            if num == expected:
                sections.append((current_label, "\n".join(buf)))
                current_label = str(num)
                buf = []
                expected += 1
            else:
                warnings.append(
                    f"第 {lineno} 行“{line.strip()}”不是下一个章节号"
                    f"（期望 {expected}），已当作正文处理"
                )
                buf.append(line)
        else:
            buf.append(line)
    sections.append((current_label, "\n".join(buf)))
    sections = [(l, t) for l, t in sections if clean(t)]

    chapters = [(l, t) for l, t in sections if l != "引言"]
    if not chapters:
        print("错误：未识别到任何章节号，无法计数。", file=sys.stderr)
        print(
            "输入格式要求：引言在前，章节号单独一行，格式为 1、第1章、第一章、1. 或 1、，"
            "且从 1 开始按顺序递增；标题请用 '# ' 开头或不要放标题行。",
            file=sys.stderr,
        )
        return 2

    rows = []
    for label, text in sections:
        total = len(clean(text))
        dlg = dialogue_chars(text)
        rows.append((label, total, dlg, dlg / total if total else 0))

    print(f"{'章节':>6} {'字数':>6} {'对话字数':>8} {'对话占比':>8}  {'范围':>6}")
    for label, total, dlg, ratio in rows:
        if label == "引言":
            f = flag(total, INTRO_MIN, INTRO_MAX)
        else:
            f = flag(total, CHAPTER_MIN, CHAPTER_MAX)
        print(f"{label:>6} {total:>6} {dlg:>8} {ratio:>7.0%}  {f}")
    for w in warnings[:10]:
        print(f"警告：{w}")
    if len(warnings) > 10:
        print(f"警告：另有 {len(warnings) - 10} 条同类警告已省略")

    counts = [r[1] for r in rows if r[0] != "引言"]
    out_of_range = sum(1 for c in counts if c < CHAPTER_MIN or c > CHAPTER_MAX)
    print(
        f"\n正文合计: {sum(counts)} 字, 章数: {len(counts)}, "
        f"平均每章: {sum(counts) / len(counts):.1f} 字, "
        f"最短: {min(counts)} 字, 最长: {max(counts)} 字, "
        f"超范围章数: {out_of_range}"
    )
    if rows:
        print(f"全文合计（含引言）: {sum(r[1] for r in rows)} 字")

    if args.anchor_chapter is not None:
        labels = [r[0] for r in rows]
        if str(args.anchor_chapter) not in labels:
            print(f"\n截断点：锚点章节 {args.anchor_chapter} 尚未出现，不计算比例。")
        else:
            total_all = sum(r[1] for r in rows)
            upto = 0
            for label, total, _dlg, _ratio in rows:
                upto += total
                if label == str(args.anchor_chapter):
                    break
            share = upto / total_all if total_all else 0
            status = "在 35%-55% 内" if 0.35 <= share <= 0.55 else "不在 35%-55% 内"
            print(
                f"\n截断点：锚点章节 {args.anchor_chapter}，"
                f"锚点前累计 {upto} 字，占全文 {share:.1%}，{status}。"
            )
            print(
                "注意：全篇未写完时，这个比例只是已写部分的比例，"
                "最终判定以全篇写完后的计算为准。"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

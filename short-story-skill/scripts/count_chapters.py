#!/usr/bin/env python3
"""Count a short-story manuscript.

Input format (strict, fail loudly on mismatch):
  - Script input is always the cumulative manuscript (intro + all chapters
    written so far), NOT a batch-only file. A batch-only file (e.g. only
    chapters 5-8) must be counted with --start-chapter 5, or merged into
    the cumulative file first.
  - Optional title: a first line starting with '# ' is excluded from counts,
    EXCEPT when that line is itself a chapter marker (e.g. '# 1' is a chapter,
    not a title). Do NOT put a bare title on the first line; it will be
    counted as intro.
  - Intro: text before the first chapter marker, no title.
  - Chapter markers, one per line, in increasing order, by default starting
    at 1 (or at --start-chapter N for a batch file):
      1
      第1章 / 第一章 / 第1章 重逢 / 第1章重逢（章名与章号之间可无空格）
      第 1 章
      1. / 1. 重逢
      1、
      # 1 / # 1 重逢
    A marker line's trailing chapter title is excluded from counts, like the
    marker itself.
    Anything else is body text, not a marker. In particular, a line like
    "3 / 2 / 1" is NOT a marker, and a bare "3" that is not the next
    expected chapter number is treated as body text with a warning,
    not silently as a new chapter.

Counting: Chinese characters and punctuation, excluding chapter-marker
lines and blank lines / whitespace. Dialogue = characters inside “ ”.

Usage:
  python3 count_chapters.py <file.txt|file.md> [--anchor-chapter N]
        [--start-chapter N]
    --anchor-chapter N: the cutoff-anchor chapter. Its cumulative count is
      intro + anchor chapter + all chapters before it; the cutoff point is
      AFTER the anchor chapter, and the anchor chapter itself is included.
      If that chapter is in the file, print that cumulative share and flag
      whether it is in 35%-55%. If it is not in the file yet, print
      "截断点尚未出现" instead of inventing a share.
      IMPORTANT: this share is only a decision AFTER the whole draft is
      finished. While drafting, the anchor chapter's share is necessarily
      near 100% when it is first written and only falls as later chapters
      are added, so a per-batch share must be ignored, not acted on.
      During drafting, the anchor is defined by plot (irreversible choice /
      core truth revealed / conflict escalation to a point of no return),
      and its chapter number is a soft target on the state card, revisable.
    --start-chapter N: first chapter number expected in the file (default 1).
      Use it only for a batch-only file; the normal input is cumulative.

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
    re.compile(r"^#\s*(\d+)(?:\s+.*)?$"),
    re.compile(r"^第\s*(\d+)\s*章(?:.*)?$"),
    re.compile(r"^(\d+)[\.、](?:\s+.*)?$"),
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
    m = re.match(r"^第\s*([一二三四五六七八九十]+)\s*章(?:.*)?$", s)
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
    ap.add_argument("--start-chapter", type=int, default=1)
    ap.add_argument("--final", action="store_true",
                    help="only with --final is the cutoff share a verdict; "
                    "without it, the share is a draft reference/forecast only")
    ap.add_argument("--soft-total-chapters", type=int, default=None,
                    help="soft target total chapters for a forecast share; "
                    "forecast = estimated anchor cumulative / "
                    "(intro + soft total * average written chapter length)")
    args = ap.parse_args()

    raw = Path(args.file).read_text(encoding="utf-8")
    lines = raw.splitlines()
    # A '# ' first line is a title ONLY if it is not itself a chapter marker
    # ('# 1' is a chapter, not a title).
    if lines and lines[0].strip().startswith("# ") and parse_marker(lines[0]) is None:
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]

    sections = []
    current_label = "引言"
    buf: list[str] = []
    expected = args.start_chapter
    warnings: list[str] = []
    suspected = re.compile(r"^第.*章|^#\s*\d+|^\d+[\.、]")
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
                    f"（期望 {expected}），已当作正文处理；"
                    f"请先检查前一章的章节行是否被识别为章节号"
                )
                buf.append(line)
        else:
            if suspected.match(line.strip()):
                warnings.append(
                    f"第 {lineno} 行疑似章节行“{line.strip()}”未被识别为章节号，"
                    f"已当作正文处理；请检查格式（建议用“第N章 标题”带空格，"
                    f"或纯数字章节号）"
                )
            buf.append(line)
    sections.append((current_label, "\n".join(buf)))
    sections = [(l, t) for l, t in sections if clean(t)]

    chapters = [(l, t) for l, t in sections if l != "引言"]
    if not chapters:
        print("错误：未识别到任何章节号，无法计数。", file=sys.stderr)
        print(
            "输入格式要求：引言在前，章节号单独一行，格式为 1、第1章、第一章、"
            "第1章 重逢、1. 或 1、，且按顺序递增；正常输入是累计全文（从第 1 章"
            "开始），只含后几章的批次文件请加 --start-chapter N；标题请用 '# ' "
            "开头或不要放标题行（'# 1' 是章节号，不是标题）。",
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
        if args.start_chapter != 1:
            print(
                f"\n截断点：批次文件（从第 {args.start_chapter} 章开始）无法算全篇占比，"
                "锚点比例需要累计全文，请对累计全文跑 --anchor-chapter，"
                "此处不输出批次比例，避免误导。"
            )
        elif str(args.anchor_chapter) not in labels:
            if args.soft_total_chapters and not args.final:
                intro = next((r[1] for r in rows if r[0] == "引言"), 0)
                ch_counts = [r[1] for r in rows if r[0] != "引言"]
                avg = sum(ch_counts) / len(ch_counts) if ch_counts else 0
                denom = intro + args.soft_total_chapters * avg
                numer = intro + args.anchor_chapter * avg
                forecast = numer / denom if denom else 0
                print(
                    f"\n截断点（草稿阶段，预估，非判定）：锚点章节 {args.anchor_chapter} 尚未出现，"
                    f"预估锚点累计约 {numer:.0f} 字（引言 + 锚点章号 × 平均章长 {avg:.0f} 字），"
                    f"预估全篇约 {denom:.0f} 字（引言 + 软目标 {args.soft_total_chapters} 章 × 平均章长），"
                    f"预估占比 {forecast:.1%}；预估偏离 35%-55% 时只作提前预警，"
                    "判定只在全篇写完后用 --final 做。"
                )
            else:
                print(f"\n截断点：锚点章节 {args.anchor_chapter} 尚未出现，不计算比例。")
        else:
            total_all = sum(r[1] for r in rows)
            upto = 0
            for label, total, _dlg, _ratio in rows:
                upto += total
                if label == str(args.anchor_chapter):
                    break
            if args.final:
                share = upto / total_all if total_all else 0
                status = "在 35%-55% 内" if 0.35 <= share <= 0.55 else "不在 35%-55% 内"
                print(
                    f"\n截断点（全篇写完，判定）：锚点章节 {args.anchor_chapter}，"
                    f"锚点累计（含锚点章） {upto} 字，占全文 {share:.1%}，{status}。"
                )
            elif args.soft_total_chapters:
                intro = next((r[1] for r in rows if r[0] == "引言"), 0)
                ch_counts = [r[1] for r in rows if r[0] != "引言"]
                avg = sum(ch_counts) / len(ch_counts) if ch_counts else 0
                denom = intro + args.soft_total_chapters * avg
                # numerator: actual if anchor written (it is, here), else estimate
                forecast = upto / denom if denom else 0
                print(
                    f"\n截断点（草稿阶段，预估，非判定）：锚点章节 {args.anchor_chapter}，"
                    f"锚点累计（含锚点章） {upto} 字，预估全篇约 {denom:.0f} 字"
                    f"（引言 + 软目标 {args.soft_total_chapters} 章 × 平均章长 {avg:.0f} 字），"
                    f"预估占比 {forecast:.1%}；预估偏离 35%-55% 时只作提前预警，"
                    "不要按它改已评审的批次，判定只在全篇写完后用 --final 做。"
                )
            else:
                share = upto / total_all if total_all else 0
                print(
                    f"\n截断点（草稿阶段，仅参考，不判定）：锚点章节 {args.anchor_chapter}，"
                    f"锚点累计（含锚点章） {upto} 字，占已写部分 {share:.1%}；"
                    "锚点刚写完时这个数字必然接近 100%，请忽略，不要照着改。"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

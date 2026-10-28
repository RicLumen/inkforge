#!/usr/bin/env python3
"""Count a short-story manuscript in the author's format.

Usage: python3 count_chapters.py <file.txt|file.md>
Format: intro (no title) followed by chapters numbered on their own line:
    1
    ...text...
    2
    ...text...
Counting rule (same as SKILL.md): count Chinese characters and punctuation,
exclude chapter-number lines and blank lines / whitespace.
Also reports dialogue ratio: characters inside “ ” / total characters.
"""
import re
import sys
from pathlib import Path


def clean(text: str) -> str:
    return re.sub(r"\s+", "", text)


def dialogue_chars(text: str) -> int:
    parts = re.findall(r"“([^”]*)”", text)
    return sum(len(clean(p)) for p in parts)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: count_chapters.py <file>", file=sys.stderr)
        raise SystemExit(2)
    raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    lines = raw.splitlines()
    # Split on lines that are only a number.
    sections = []  # (label, text)
    current_label = "引言"
    buf: list[str] = []
    for line in lines:
        if re.fullmatch(r"\d+", line.strip()):
            sections.append((current_label, "\n".join(buf)))
            current_label = line.strip()
            buf = []
        else:
            buf.append(line)
    sections.append((current_label, "\n".join(buf)))
    # Drop a leading empty intro if file starts with a number.
    sections = [(l, t) for l, t in sections if clean(t)]
    rows = []
    for label, text in sections:
        total = len(clean(text))
        dlg = dialogue_chars(text)
        rows.append((label, total, dlg, dlg / total if total else 0))
    chapters = [r for r in rows if r[0] != "引言"]
    print(f"{'章节':>6} {'字数':>6} {'对话字数':>8} {'对话占比':>8}")
    for label, total, dlg, ratio in rows:
        print(f"{label:>6} {total:>6} {dlg:>8} {ratio:>7.0%}")
    if chapters:
        counts = [c[1] for c in chapters]
        print(f"\n正文合计: {sum(counts)} 字, 章数: {len(counts)}, "
              f"平均每章: {sum(counts) / len(counts):.1f} 字, "
              f"最短: {min(counts)} 字, 最长: {max(counts)} 字")
    if rows:
        print(f"全文合计（含引言）: {sum(r[1] for r in rows)} 字")


if __name__ == "__main__":
    main()

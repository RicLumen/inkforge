#!/usr/bin/env python3
"""Check that documentation pointers in the skill actually resolve.

This script exists because v0.7 accidentally deleted the whole
"正文规则" section from SKILL.md while splitting another section, and
no test caught it: SKILL.md, writer.md, skeleton.md and both READMEs
kept pointing at a heading that no longer existed.

Checks (exit 1 on any failure, 0 when clean):
  1. Every "见下面“X”" / "见 SKILL.md X" / "上面的正文规则" style pointer
     in *.md files resolves to a heading in SKILL.md (a heading counts
     if it contains the target text, so "正文规则" matches
     "## 正文规则（自包含，…）").
  2. Every `references/*.md`, `prompts/*.md`, `scripts/*.py` file reference
     in *.md files exists on disk.
  3. writer.md and skeleton.md repeat the key chapter/intro numbers, so
     an isolated writing session is not left with only a pointer.

Usage: python3 scripts/check_pointers.py [--root <skill-dir>]
  Default root is the skill directory containing this script's parent.
  CHANGELOG.md is excluded: it is history, and may mention sections
  that existed at the time of writing.
"""
import argparse
import re
import sys
from pathlib import Path

HEADING_POINTERS = [
    re.compile(r"见下面[“‘\"']([^”’\"'，。]+)"),
    re.compile(r"见\s*SKILL\.md\s*([^，。、\n]+)"),
    re.compile(r"上面的(正文规则)"),
    re.compile(r"遵守上面的(正文规则)"),
]
FILE_POINTERS = [
    re.compile(r"`(references/[^`\s]+\.md)`"),
    re.compile(r"`(prompts/[^`\s]+\.md)`"),
    re.compile(r"`(scripts/[^`\s]+\.py)`"),
    re.compile(r"(references/[^`\s]+\.md)"),
    re.compile(r"(scripts/[^`\s]+\.py)"),
]


def clean_target(raw: str) -> str:
    t = raw.strip().strip("：:、")
    # "软目标一节" -> "软目标", "补字数规则" stays, "正文规则" stays.
    t = re.sub(r"(一节|一章)$", "", t)
    # "SKILL.md 正文规则" style: take the last token.
    t = t.split()[-1] if t.split() else t
    return t.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    skill = root / "SKILL.md"
    if not skill.exists():
        print(f"错误：{skill} 不存在", file=sys.stderr)
        return 1
    headings = []
    for line in skill.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{1,3}\s+(.*)$", line.strip())
        if m:
            headings.append(m.group(1).strip())
    failures = []
    md_files = sorted(p for p in root.rglob("*.md") if p.name != "CHANGELOG.md")
    for f in md_files:
        text = f.read_text(encoding="utf-8")
        for pat in HEADING_POINTERS:
            for m in pat.finditer(text):
                target = clean_target(m.group(1))
                if not target or target in ("SKILL.md", "SKILL"):
                    continue
                if not any(target in h or h.split("（")[0].strip() == target for h in headings):
                    failures.append(f"{f.relative_to(root)}: 指针“{target}”在 SKILL.md 里没有对应标题")
        for pat in FILE_POINTERS:
            for m in pat.finditer(text):
                rel = m.group(1)
                if not (root / rel).exists():
                    failures.append(f"{f.relative_to(root)}: 文件指针“{rel}”不存在")
    for role in ("prompts/writer.md", "prompts/skeleton.md"):
        text = (root / role).read_text(encoding="utf-8")
        if "500" not in text or "1000" not in text:
            failures.append(f"{role}: 独立会话关键数字缺失（应含单章 500–1000 字）")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print(f"OK: {len(md_files)} 个文档文件，指针与独立会话数字检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

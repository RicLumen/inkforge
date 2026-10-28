#!/usr/bin/env python3
"""Check that documentation pointers and key content in the skill survive.

v0.8's checker only proved headings existed. Claude's v0.8 review showed
four blind spots, each reproduced here as a check:
  1. Heading present, body emptied -> the 正文规则 section must keep a
     minimum body length AND contain the anchor definition.
  2. Anchor definition deleted -> a key-phrase list must be present
     somewhere in the docs (not just a heading).
  3. Pointers written as 遵守/按/依据/详见, not only 见 -> all of those
     verb patterns are matched, and a pointer to a named file must
     resolve in that file.
  4. Number check was presence-only -> role prompts must contain the
     same chapter numbers found in SKILL.md, and conceiver.md is covered.

Usage: python3 scripts/check_pointers.py [--root <skill-dir>]
  Default root is the skill directory containing this script's parent.
  CHANGELOG.md is excluded: it is history, and may mention sections
  that existed at the time of writing. Exit 1 on any failure.
"""
import argparse
import re
import sys
from pathlib import Path

# Phrases that must exist somewhere in the docs. Deleting any one of
# them (e.g. the anchor definition) is a content regression even if
# every heading still exists.
KEY_PHRASES = [
    "唯一完整定义",   # anchor definition, SKILL.md 正文规则 only
    "字数计数办法",
    "弯引号",
    "硬线",
    "锚点累计",
    "35%-55%",
    "软目标",
    "累计未收伏笔",
    "全文自洽",
]

POINTER_PATTERNS = [
    re.compile(r"见下面[“‘\"']([^”’\"'，。]+)"),
    re.compile(r"见\s*`?(SKILL\.md|references/[^`\s]+\.md)`?\s+([^，。、\n]+)"),
    re.compile(r"(?:按|遵守|依据|详见|参考)\s*`?(SKILL\.md|references/[^`\s]+\.md)`?\s+([^，。、\n]+)"),
    re.compile(r"(?:按|遵守|依据)\s*上面的(正文规则)"),
    re.compile(r"SKILL\.md\s+(正文规则|补字数规则|对话软警告|软目标[^，。]*|计数办法)"),
]
FILE_PATTERNS = [
    re.compile(r"`(references/[^`\s]+\.md)`"),
    re.compile(r"`(prompts/[^`\s]+\.md)`"),
    re.compile(r"`(scripts/[^`\s]+\.py)`"),
    re.compile(r"(references/[^`\s]+\.md)"),
    re.compile(r"(scripts/[^`\s]+\.py)"),
]
ROLE_FILES = ["prompts/writer.md", "prompts/skeleton.md", "prompts/conceiver.md"]


def clean_target(raw: str) -> str:
    t = raw.strip().strip("：:、；")
    t = re.sub(r"(一节|一章)$", "", t)
    # Keep up to a rule/section keyword, drop trailing verbs like 为准/执行/来.
    for kw in ("规则", "办法", "清单", "核对", "警告", "排锚点"):
        idx = t.find(kw)
        if idx != -1:
            t = t[: idx + len(kw)]
            break
    else:
        t = t.split()[0] if t.split() else t
    return t.strip()


def headings_of(text: str):
    out = []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)$", line.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def section_body(text: str, heading_substr: str):
    lines = text.splitlines()
    start = end = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and heading_substr in line:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    failures = []
    skill = root / "SKILL.md"
    if not skill.exists():
        print(f"错误：{skill} 不存在", file=sys.stderr)
        return 1
    md_files = sorted(p for p in root.rglob("*.md") if p.name != "CHANGELOG.md")
    all_text = {f: f.read_text(encoding="utf-8") for f in md_files}
    headings_by_file = {f: headings_of(t) for f, t in all_text.items()}
    all_headings = [h for hs in headings_by_file.values() for h in hs]

    # 1. Key phrases must exist somewhere.
    joined = "\n".join(all_text.values())
    for phrase in KEY_PHRASES:
        if phrase not in joined:
            failures.append(f"关键短语缺失：{phrase}（全库任何文档里都没有）")
    # 2. 正文规则 body must not be emptied, and must hold the anchor definition.
    body = section_body(all_text[skill], "正文规则")
    if body is None:
        failures.append("SKILL.md 里没有“正文规则”标题")
    else:
        non_empty = [ln for ln in body.splitlines() if ln.strip() and not ln.startswith("## ")]
        if len(non_empty) < 10 or len(body) < 1000:
            failures.append(f"“正文规则”正文只有 {len(non_empty)} 行非空行、{len(body)} 字，疑似内容被清空")
        if "唯一完整定义" not in body:
            failures.append("“正文规则”正文里没有锚点的“唯一完整定义”")
    # 3. Heading pointers, across 见/按/遵守/依据/详见/参考.
    for f, text in all_text.items():
        rel = str(f.relative_to(root))
        for pat in POINTER_PATTERNS:
            for m in pat.finditer(text):
                groups = [g for g in m.groups() if g]
                if len(groups) >= 2 and (groups[0].endswith(".md")):
                    _t = clean_target(groups[1])
                    if not any(kw in _t for kw in ("规则", "办法", "清单", "核对", "警告", "排锚点", "正文规则")):
                        continue
                    fname, raw_target = groups[0], groups[1]
                    target = clean_target(raw_target)
                    if not target:
                        continue
                    target_file = root / fname
                    if not target_file.exists():
                        failures.append(f"{rel}: 指针文件“{fname}”不存在")
                    else:
                        hs = headings_by_file.get(target_file, [])
                        if not any(target in h or h.split("（")[0].strip() == target for h in hs):
                            failures.append(f"{rel}: 指针“{target}”在 {fname} 里没有对应标题")
                else:
                    target = clean_target(groups[-1])
                    if not target or target in ("SKILL.md", "SKILL"):
                        continue
                    if not any(kw in target for kw in ("规则", "办法", "清单", "核对", "警告", "排锚点", "正文规则")):
                        continue
                    if not any(target in h or h.split("（")[0].strip() == target for h in all_headings):
                        failures.append(f"{rel}: 指针“{target}”在全库里没有对应标题")
        for pat in FILE_PATTERNS:
            for m in pat.finditer(text):
                if not (root / m.group(1)).exists():
                    failures.append(f"{rel}: 文件指针“{m.group(1)}”不存在")
    # 4. Number consistency: SKILL's chapter numbers must appear in every role prompt.
    skill_text = all_text[skill]
    for num in ("500", "1000"):
        if num not in skill_text:
            failures.append(f"SKILL.md 里找不到单章数字 {num}")
            continue
        for role in ROLE_FILES:
            if num not in all_text[root / role]:
                failures.append(f"{role}: 缺少与 SKILL.md 一致的单章数字 {num}")
    if "15%" not in all_text[root / "prompts/reviewer.md"]:
        failures.append("prompts/reviewer.md: 缺少对话警告数字 15%")
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print(f"OK: {len(md_files)} 个文档文件，指针、关键短语与数字一致性检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

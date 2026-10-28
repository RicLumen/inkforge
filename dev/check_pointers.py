#!/usr/bin/env python3
"""Check the skill docs: every referenced file exists, and the key
numbers in each role prompt also appear in SKILL.md.

Run from the repo root: python3 dev/check_pointers.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "short-story-skill"
PATH = re.compile(r"(?:references|prompts|scripts)/[\w.-]+\.(?:md|py)")
NUMBERS = {
    "prompts/writer.md": ["500", "1000", "15%"],
    "prompts/conceiver.md": ["500", "1000"],
    "prompts/reviewer.md": ["500", "15%"],
}

failures = []
for f in sorted(ROOT.rglob("*.md")):
    for p in PATH.findall(f.read_text(encoding="utf-8")):
        if not (ROOT / p).exists():
            failures.append(f"{f.relative_to(ROOT)}: 引用的 {p} 不存在")
skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
for prompt, nums in NUMBERS.items():
    text = (ROOT / prompt).read_text(encoding="utf-8")
    for n in nums:
        if n not in skill or n not in text:
            failures.append(f"{prompt}: 数字 {n} 与 SKILL.md 不一致")
for msg in failures:
    print(f"FAIL: {msg}")
print("OK" if not failures else f"{len(failures)} 项失败")
raise SystemExit(1 if failures else 0)

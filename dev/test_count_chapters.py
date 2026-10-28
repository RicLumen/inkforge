#!/usr/bin/env python3
"""Regression tests for count_chapters.py, using synthetic samples.

Run from the repo root: python3 dev/test_count_chapters.py
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "short-story-skill/scripts/count_chapters.py"


def run(text, args=()):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "t.txt"
        f.write_text(text, encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(f), *args],
                              capture_output=True, text=True)


def chapter(n, body):
    return f"\n{n}\n{body}"


class TestFormats(unittest.TestCase):
    def test_markers(self):
        text = ("引言" * 60
                + chapter("第一章", "正文。" * 200)
                + chapter("2.", "正文。" * 200)
                + chapter("# 3", "正文。" * 200)
                + chapter("第4章 重逢", "正文。" * 200)
                + chapter("第5章反转", "正文。" * 200))
        r = run(text)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("章数: 5", r.stdout)

    def test_batch_only_file_fails(self):
        text = chapter("5", "正文。" * 200) + chapter("6", "正文。" * 200)
        self.assertNotEqual(run(text).returncode, 0)


class TestDialogue(unittest.TestCase):
    def test_batch_ratio_not_hidden_by_cumulative(self):
        dlg = "“你好吗？”" * 20 + "正文。" * 100
        zero = "正文。" * 200
        text = ("引言" * 60
                + "".join(chapter(i, dlg) for i in range(1, 5))
                + "".join(chapter(i, zero) for i in range(5, 9)))
        r = run(text, ["--batch-from", "5"])
        self.assertIn("本批对话占比: 0.0%", r.stdout)
        self.assertIn("低于 15%", r.stdout)

    def test_straight_quotes_warned(self):
        r = run("引言" * 60 + chapter("1", '"你来了。"' + "正文。" * 200))
        self.assertIn("检测到直引号", r.stdout)

    def test_single_char_emphasis_not_dialogue(self):
        text = ("引言" * 60
                + chapter("1", "“沈”“影”“线”" + "正文。" * 200)
                + chapter("2", "“嗯”" + "正文。" * 200))
        self.assertIn("累计正文对话合计: 1 字", run(text).stdout)


class TestBoundsAndAnchor(unittest.TestCase):
    def test_upper_bound(self):
        text = ("引言" * 60 + chapter("1", "正文。" * 550)
                + chapter("2", "正文。" * 700))
        self.assertIn("超范围章数: 2", run(text).stdout)

    def test_final_only_verdict(self):
        text = ("引言" * 60 + chapter("1", "正文。" * 200)
                + chapter("2", "正文。" * 200))
        r = run(text, ["--anchor-chapter", "1"])
        self.assertNotIn("35%-55% 内", r.stdout)
        r = run(text, ["--anchor-chapter", "1", "--final"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("在 35%-55% 内", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)

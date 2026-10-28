# dev/

维护用，不进安装包（安装只复制 `short-story-skill/`）。

- `check_pointers.py`：检查文档里引用的文件是否存在，以及提示词里的关键数字是否与 SKILL.md 一致。
- `test_count_chapters.py`：计数脚本的测试。

在仓库根目录运行：

```
python3 dev/check_pointers.py
python3 dev/test_count_chapters.py
```

推送时 GitHub Actions 会自动跑这两项。

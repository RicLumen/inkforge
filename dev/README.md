# dev/：本地开发文件，不进安装包

这个目录里的东西只给维护仓库的人用，安装 skill 时不要复制它。
安装命令只复制 `short-story-skill/`，那个文件夹里全是运行文件，
这里的东西一个都不会到用户电脑上。

- `check_pointers.py`：文档自检，查指针、关键短语、数字一致性，改文档后必跑。
  从仓库根目录跑：`python3 dev/check_pointers.py`
- `test_count_chapters.py`：计数脚本的回归测试，9 个合成样例。
  从仓库根目录跑：`python3 dev/test_count_chapters.py`
- `test-run-01.md`：第一次试跑记录，仅第一批，梗概是助理编造的，不是作者作品，
  留着只为说明流程跑通过一次，不作为示例发给用户。

推送时 GitHub Actions 会自动跑上面两项，本地改完文档先跑通再推。

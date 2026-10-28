# short-story-skill

用评审、写作、构思三线程循环写中文短篇的 skill。篇幅与章节规格按 SKILL.md 正文规则执行，不设两档；不适用于英文短篇和纯文学短篇。

## 这个 skill 是什么

这套执行规格按批次推进：写作按构思给的方向写，评审按量表逐项打分，写作逐条修改，直到评审说不用再改才进入下一批。这样可以避免长篇在中途断线、跑偏或字数失控。

## 不设两档，只规定确定的格式

一篇短文是超短还是中短，格式和每章字数都相同。AI 往往要在写完后才能看出最终属于超短还是中短，因此本 skill 只规定确定的格式，开始前不硬定最终字数和档位。写完后的分类仅作参考，区间见 SKILL.md“不设两档”一节。

## 规格速览（只作入口，不作执行依据）

执行依据只有 SKILL.md 及其细则索引里的文件，本节不重复数字，避免两处漂移：引言与单章篇幅、每章钩子、截断点位置、情绪基调、视角、节奏、标点与规范用字，见 SKILL.md“正文规则”；软目标排锚点、字数计数办法、补字数规则、对话软警告、全篇状态卡核对，见 SKILL.md“细则索引”指向的 `references/` 文件。历史口径变更见 CHANGELOG.md。

## 文件结构

```
short-story-skill/
├── SKILL.md                  # 流程与索引：统一格式、批次、循环与终止规则，细则只写指针
├── skill.yaml                # skill 元数据
├── prompts/                  # 写作 / 评审 / 构思角色提示词与骨架（关键数字为独立会话重复）
├── scripts/
│   ├── count_chapters.py     # 字数与截断点计数脚本（输入永远是累计全文）
│   ├── check_pointers.py     # 文档自检：指针、关键短语、数字一致性，改文档后必跑
│   └── test_count_chapters.py  # 计数脚本回归测试
├── CHANGELOG.md              # 历史口径变更，不参与执行
└── references/               # 细则与量表（执行时按这些文件查）
    ├── soft-target.md        # 软目标排锚点与预估时机
    ├── counting.md           # 字数计数办法六步
    ├── padding-rules.md      # 补字数规则
    ├── dialogue-warning.md   # 对话软警告
    ├── final-audit.md        # 全篇状态卡核对与全文自洽
    ├── reviewer-rubric.md    # 八项评审量表与输出格式
    ├── state-card.md         # 批次状态卡（构思维护）
    ├── rejection-checklist.md  # 常见拒稿点清单（默认启用）
    ├── anti-ai-checklist.md  # 去 AI 味检查
    ├── submission-body-rules.md  # 背景转述，不作执行前提
    ├── stack.md              # 作者实测 AI 与 skill（作者示例，可选）
    └── platforms.md          # 作者实测发布平台（作者示例，可选）
```

## 怎么用

安装到本机，一次即可：

```
git clone https://github.com/RicLumen/inkforge
cp -r inkforge/short-story-skill ~/.claude/skills/  # Claude Code；Muse 放到 ~/workspace/custom-skills/
```

装好后直接用命令开写，把【你的剧情】换成你的剧情：

```
/short-story-skill 剧情：【你的剧情】
```

Muse 里没有斜杠命令时，直接说“用 short-story-skill 写一篇中文短篇，剧情：【你的剧情】”即可，效果一样。不能安装的网页对话，才用仓库链接那句作备用。

维护：改文档后跑 `python3 scripts/check_pointers.py` 与 `python3 scripts/test_count_chapters.py`，两项通过才能推。

## 作者示例清单（只是示例，空着不阻塞流程）

- 生成 AI：模型名、档位、为什么选它
- 润色 / 去 AI 味 skill：名字、用在哪个环节、哪一步必须人工过
- 发布平台：平台名、体量、结算路径、注意事项（只写实测过的）
- 脱敏示例：引言加前几章的改写示例，不要放真实在连载作品全文

## 边界

本 skill 不替用户决定题材，不承诺收益，不含用户真实作品、账号与收入截图。收入证明只在项目 README 中脱敏展示。
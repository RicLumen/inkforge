# ✍️ InkForge — AI 短篇网文写作 Skill

<p align="center">
  <img src="https://img.shields.io/badge/版本-v1.0.12-blue" alt="版本" />
  <img src="https://img.shields.io/badge/定位-中文短篇网文-brightgreen" alt="定位" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

InkForge 是一个中文短篇网文写作 skill，题材由你定。

## 怎么写

构思、写作、评审三个角色分批循环：

1. 构思角色给下一批的方向，并维护一张状态卡（主线、锚点、基调、视角、时间线、人物状态、未收伏笔）。
2. 写作角色按方向写一批，第一批是引言加第 1–4 章，写完用计数脚本统计累计全文的字数和对话占比。
3. 评审角色按八项量表逐项评，写作角色逐条改，评审给出“不用再改”才进下一批；同一批改到第 3 轮仍有分歧，交给用户定。
4. 全篇写完后，评审对照全文核对状态卡，查前后是否自洽，再用脚本核对截断点。

评审最好在独立子 agent 或独立会话里运行，只看本批正文、状态卡、脚本输出和量表。

## 格式要点

- 动笔前不定总字数，写完再看篇幅。
- 引言约 150 字，单章 500–1000 字，每章结尾留钩子。
- 截断点在锚点章（主角彻底决裂、亮出底牌或核心真相揭开的那一章）之后，全篇写完后应在全文 35%–55%，也就是付费卡点。
- 本批对话占比低于 15% 时，评审会点出来。

完整规则见 `short-story-skill/SKILL.md`。

## 安装

```
npx skills add RicLumen/inkforge --skill short-story-skill
```

## 使用

装好后用命令开写，后面直接说你想写什么：

```
/short-story-skill 你想写什么
```

计数脚本也可以单独运行：

```
python3 short-story-skill/scripts/count_chapters.py 全文.txt --batch-from 5
python3 short-story-skill/scripts/count_chapters.py 全文.txt --anchor-chapter 6 --final
```

## 目录

```
inkforge/
├── .github/workflows/check.yml   # 推送时跑 dev/ 里的两项检查
├── dev/                          # 维护用，不进安装包
│   ├── check_pointers.py         # 文档引用和关键数字检查
│   └── test_count_chapters.py    # 计数脚本测试
└── short-story-skill/            # 安装包
    ├── SKILL.md                  # 流程和全部规则
    ├── prompts/                  # 构思 / 写作 / 评审提示词
    ├── references/               # 评审量表、状态卡、去 AI 味检查
    └── scripts/count_chapters.py # 计数脚本
```

## 注意

AI 生成的内容发布前请人工审校，并按平台规则查原创性和敏感词。

## License

MIT，见 `LICENSE`。

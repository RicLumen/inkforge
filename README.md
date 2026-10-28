# ✍️ InkForge — AI 短篇小说写作 Skill

> **题材由你定，这里讲一篇短篇怎么一批一批写完。**
> 当前版本：v1.0.9。
> 用哪个 AI 写、配什么去 AI 味 skill、发在哪个平台，还没补上，见文末“待补”。

<p align="center">
  <img src="https://img.shields.io/badge/定位-短篇小说创作-brightgreen" alt="定位" />
  <img src="https://img.shields.io/badge/写法-评审_写作_构思三线程-blue" alt="写法" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

## 这是什么

InkForge 是一个中文短篇小说写作 skill，不限题材。

它想回答四个问题：用什么 AI 写、配什么 skill 去 AI 味、小说按什么结构写、写完发哪里。现在写好的是结构这一块，其余三个见“待补”。

写法是构思、写作、评审三个角色分批循环：构思给方向，写作写一批，评审按八项量表打分，写作逐条改，评审说“不用再改”才进下一批。

## 写作格式

动笔前不定总字数，写完再看篇幅。固定的只有这些：单章 500–1000 字，引言约 150 字，每章结尾留钩子，截断点在全文 35%–55%（全篇写完后用脚本核对）。完整规则见 `short-story-skill/SKILL.md`。

## 快速开始

```
npx skills add RicLumen/inkforge --skill short-story-skill
```

装好后用命令开写，后面直接说你想写什么：

```
/short-story-skill 你想写什么
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

## 待补

- 用哪个 AI、什么档位，配哪个去 AI 味 / 润色 skill：等对比测试。计划用同一段 prompt 让 GPT、Claude、Gemini 各写一小段，再分别比较用和不用 humanizer-zh，由人工评判。测试还没做，这里先空着。
- 实测过的发布平台：待补。
- 脱敏示例：待补，不放连载作品全文，收入只做脱敏展示。

## 边界

- 只分享方法，不承诺收益。
- AI 生成的内容发布前请人工审校，并按平台规则查原创性。

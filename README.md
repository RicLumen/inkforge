# ✍️ InkForge — AI 短篇小说方法 Skill

> **题材由你定，这里只讲一篇短篇是怎么跑通的。**
> 当前版本：v0.9.3。
> 欢迎试用并反馈，作者示例栈、发布平台与脱敏示例仍在补齐中。

<p align="center">
  <img src="https://img.shields.io/badge/定位-短篇小说创作-brightgreen" alt="定位" />
  <img src="https://img.shields.io/badge/写法-评审_写作_构思三线程-blue" alt="写法" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</p>

## 这是什么

InkForge 是一个中文短篇小说写作 skill。

它回答短篇创作者最实际的问题：选择什么 AI 进行创作、搭配什么 skill 去ai味、小说按什么结构写、写完发哪里有人看。不限题材、不限脑洞、不限人物与世界观。

核心是三线程写法：写作按构思给的方向写一批，评审按量表逐项打分，写作逐条改，改到评审说不用再改才进下一批。

## 统一写作格式

AI 不擅长预先定死最终字数，往往写完才能确定篇幅，因此本项目只规定确定的部分，不在开始写作前硬性规定最终字数。

具体格式（单章篇幅与上下限、引言、每章钩子、截断点位置、基调、视角、节奏、标点与规范用字）以 `short-story-skill/SKILL.md`“正文规则”与“细则索引”为准，本 README 不重复数字，避免两处漂移。付费截断点按情节锚点定在全文 35%-55%，锚点是主角做出不可逆选择、核心真相揭开，或主冲突升级到无法回头的那一刻；截断点只在全篇写完后用脚本 `--final` 核对，逐批不判。

写完之后再分类，仅供参考，分类区间见 SKILL.md“不设两档”一节。

## 结构说明

- `short-story-skill/SKILL.md`：流程与索引——三线程分工、批次推进、循环与终止规则，细则只写指针，不展开。
- `short-story-skill/references/`：细则——软目标排锚点、字数计数办法、补字数规则、对话软警告、全篇状态卡核对、八项量表、状态卡、拒稿清单。
- `short-story-skill/prompts/`：写作、评审、构思角色提示词与骨架，关键数字为独立会话重复。
- `short-story-skill/scripts/`：计数脚本、文档自检脚本、计数脚本回归测试。
- `.github/workflows/check.yml`：每次推送自动跑文档自检与计数回归测试。

## 快速开始

安装到本机，一次即可：

```
git clone https://github.com/RicLumen/inkforge
cp -r inkforge/short-story-skill ~/.claude/skills/  # Claude Code；Muse 放到 ~/workspace/custom-skills/
```

装好后直接用命令开写，把【你的剧情】换成你的剧情：

```
/short-story-skill 剧情：【你的剧情】
```

Muse 里没有斜杠命令时，直接说“用 short-story-skill 写一篇中文付费短篇，剧情：【你的剧情】”即可，效果一样。不能安装的网页对话，才用仓库链接那句作备用。

## 目录

```
inkforge/
├── .github/workflows/check.yml   # 推送时自动跑文档自检与计数回归测试
├── docs/test-run-01.md           # 第一次试跑记录（仅第一批，助理编造梗概，非作者作品）
└── short-story-skill/
    ├── SKILL.md                  # 流程与索引
    ├── skill.yaml                # skill 元数据
    ├── prompts/                  # 写作 / 评审 / 构思角色提示词与骨架
    ├── scripts/                  # 计数脚本、自检脚本、回归测试
    ├── CHANGELOG.md              # 历史口径变更
    └── references/               # 细则：软目标、计数、补字数、对话警告、最终核对、量表等
```

## 常见拒稿点

主线不清晰、矛盾冲突悬浮、整体节奏慢、场景心理外貌描写过多且无信息增量、钩子不足。详情见 `short-story-skill/references/rejection-checklist.md`。

## 状态与待填

本仓库当前为 v0.9.2，核心流程可用，尚未发布完整示例。

待补清单（只是示例，空着不阻塞流程）：作者示例 AI 与档位、润色用的 skill、实测过的发布平台、脱敏示例。示例不会放真实在连载作品全文，收入证明只会脱敏展示。

## 边界

- 本项目分享的是方法，不承诺收益；作者个人收益不代表读者能达到同样收益。
- 示例均为脱敏改写。
- AI 生成内容请按发布平台规则做人工审校与原创性检查。

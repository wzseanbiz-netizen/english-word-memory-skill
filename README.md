# 英语单词双法记忆 · Dual-Method English Word Memory

一个技能包（Agent Skill）：对每个英语单词**同时给出两版独立记忆方案**，并列展示、对比择优。

- **方法一 · 联想记忆法** — 把单词拆成熟悉碎片，用熟词 / 拼音 / 编码 / 谐音映射到中文画面，焊成一句越荒诞越通感越好记的串联句。
- **方法二 · 词根词缀记忆法** — 拆「前缀 + 词根 + 后缀」，由词素义推导词义。

两版各自闭环，**同一版内不混写**：联想版不掺词素推导，词素版不掺荒诞画面。某法不适用时标注「不适用」并说明原因。

> An agent skill that produces **two independent mnemonic plans** for each English word — an associative one (familiar words, pinyin, letter codes, homophones woven into a vivid sentence) and a morphological one (prefix + root + suffix) — shown side by side for comparison.

---

## 安装

克隆到 skills 目录即可（仓库根即 skill 包）：

```bash
git clone https://github.com/wzseanbiz-netizen/english-word-memory-skill.git \
  ~/.workbuddy/skills/english-word-memory
```

也可复制到任意支持 `SKILL.md` 的 Agent 技能目录（Claude Code、Cursor、Codex 等）。

无第三方依赖。`scripts/word_memory.py` 仅用 Python 3 标准库。

## 用法

触发即可，无需命令：

- 帮我记一下 `transportation` 这个单词
- 用两种方法给我记 `suppose`、`birthmark`、`bright`
- 给 `accommodation` 编个记忆法
- 批量：一行一个单词，或 `word | 释义 | 词性`

输出结构：

```text
【word】释义（词性）

▍方法一 · 联想记忆法
切分：…（2–3 段，按原字母顺序）
译码：…（每段标注 熟词/拼音/编码/谐音）
碎片意象：…（每段一个荒诞镜头）
串联成句：…（一句，词义融进画面）
复习：当天 / 隔天 / 每周

▍方法二 · 词根词缀记忆法
拆词素：前缀 + 词根 + 后缀
解义 / 组义 / 锚定
复习：当天 / 隔天 / 每周

▍择优建议：该词更适合哪版、为什么
```

### 机械辅助（可选）

脚本不编含义，只做机械匹配，创意仍由 Agent 完成：

```bash
python3 scripts/word_memory.py transportation            # 联想法：切分候选 + 译码建议
python3 scripts/word_memory.py transport --mode affix    # 词根词缀：自动匹配前后缀
```

实测输出（联想法）：

```text
步骤1 切分候选:
  · 片段 'po'  →  婆 [谐音]  (例: Point)
  · 片段 'tr'  →  训/练 [熟词]  (例: training)
```

## 目录

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 技能定义：两种方法的完整步骤、成句五条硬规则、红线 |
| `references/framework.md` | 方法论原理与「事实 / 推测」边界 |
| `references/examples.md` | 已验证的成句示例 |
| `references/encoding.md` | 英文编码表（字母 / 组合 → 中文意象） |
| `references/affix.md` | 词根词缀精简词素表 |
| `scripts/word_memory.py` | 切分 / 译码 / 词素匹配的机械辅助 |
| `scripts/mapping.json` | 机械切分与译码库（含 `encoding`、`affix` 段） |

## 几条硬约束（节选自 SKILL.md）

1. **熟词真义铁律** — 标「熟词」的片段，其中文必须是该英文片段本身的字典常用义。`an` 是「一个」不是「在」；`ex` 不是「儿媳」。错了会误人子弟，对不上就改标「编码」。
2. **字母全覆盖** — 拆分后每段译码必须覆盖该段全部字母，不得漏译；孤立单辅音尾并入相邻模块。
3. **不逐字母拆** — 段数越少越好，通常 2–3 段、最多 4 段。为用编码法而逐字母拆开，会让人更难记。
4. **模块顺序锁定** — 拆分模块按单词原字母顺序出现，不得跳序。
5. **词义融合** — 中文词义要成为画面里活着的角色，不能句尾甩标签「——这就是 X」。
6. **只编一句** — 越长越稀释情绪。荒诞 → 通感 → 刺激 → 威胁感，强度逐级叠加。

## 适用与不适用

- **小学**（词短具象）：以方法一为主，拼音首字母 + 象形，1–2 个片段，句子生活化。
- **初中**（词长抽象）：派生词用方法二独立推导；词形不透明的回方法一。
- **同族词**：方法二优先，按词根 / 前后缀成组效率最高。
- **不适用**：不负责发音教学、语法讲解、整句翻译；不为单词编造与发音 / 拼写无关的联想。

## 许可

MIT。词根词缀表属通用英语形态学常识，可随教学增删。

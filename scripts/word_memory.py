# -*- coding: utf-8 -*-
"""
单词记忆 · 机械步骤辅助脚本（七步框架第 1–3 步 + 第 4–5 步提示）

用法:
  python3 word_memory.py <word> [--meaning "中文释义"] [--pos "词性"] [--example "例句"] [--mode assoc|affix]

功能:
  - 联想法(默认 assoc)：在 mapping.json 中查找单词内出现的词音片段，给出「译码」候选汉字与方法；另输出固定「英文编码」意象序列（仅作四法之一候选：优先熟词/拼音把大块并成好记中文，勿为编码而逐字母拆，模块越少越好）。
  - 词根词缀法(affix)：自动匹配已知前缀/后缀，输出词素拆解（词根查 references/affix.md）。
  - 仅做机械匹配，不编造含义；荒诞/通感/恐怖的创意成句由调用方完成。

依赖: 仅标准库 (json, argparse, os)。
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(HERE, "mapping.json")

METHOD_ORDER = {"熟词": 0, "拼音": 1, "谐音": 2, "编码": 3}


def load_map():
    with open(MAP_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", []), data.get("encoding", {}), data.get("affix", {}), data.get("pinyin", {})


def double_letter_candidates(word, pinyin, encoding):
    """找单词中的双写字母段，给出「拼音首字母」与「编码复数」两条候选（选型见输出提示）。"""
    w = word.lower()
    singles = encoding.get("single", {})
    found = []
    seen = set()
    for i in range(len(w) - 1):
        pair = w[i:i + 2]
        if pair[0] == pair[1] and pair[0].isalpha() and pair not in seen:
            seen.add(pair)
            py = pinyin.get(pair) if isinstance(pinyin.get(pair), dict) else None
            found.append((pair, py, singles.get(pair[0], "□未编码")))
    return found


def encode_word(word, encoding):
    """用固定『英文编码表』把单词转成意象序列：组合优先、单字母兜底，覆盖全部字母。"""
    w = word.lower()
    singles = encoding.get("single", {})
    combos = encoding.get("combo", {})
    combo_sorted = sorted(combos.keys(), key=len, reverse=True)
    result = []
    i = 0
    while i < len(w):
        matched = None
        for c in combo_sorted:
            if w[i:i + len(c)] == c:
                matched = c
                break
        if matched:
            result.append((matched, combos[matched]))
            i += len(matched)
        else:
            ch = w[i]
            result.append((ch, singles.get(ch, "□未编码")))
            i += 1
    return result


def find_chunks(word, entries):
    """返回单词中命中的片段（按长度降序），每片段附候选信息。"""
    w = word.lower()
    hits = [e for e in entries if e["chunk"].lower() and e["chunk"].lower() in w]
    hits.sort(key=lambda e: len(e["chunk"]), reverse=True)
    return hits


def affix_word(word, affix):
    """词根词缀法拆解：匹配已知前缀(词首最长)与后缀(词尾最长)，返回中间词根。

    词根内部匹配不可靠，故不在脚本自动判定，留由智能体查 references/affix.md 的词根表。
    """
    w = word.lower()
    pre_list = affix.get("prefix", [])
    suf_list = affix.get("suffix", [])
    pre_sorted = sorted([p["affix"] for p in pre_list], key=len, reverse=True)
    suf_sorted = sorted([s["affix"] for s in suf_list], key=len, reverse=True)

    prefix = ""
    for p in pre_sorted:
        if w.startswith(p):
            prefix = p
            break
    rest = w[len(prefix):]

    suffix = ""
    for s in suf_sorted:
        if rest.endswith(s) and len(s) < len(rest):
            suffix = s
            break
    root = rest[:len(rest) - len(suffix)] if suffix else rest
    return prefix, root, suffix, pre_list, suf_list


def print_affix(word, affix, meaning, pos, example):
    prefix, root, suffix, pre_list, suf_list = affix_word(word, affix)
    print("=" * 48)
    print("【%s】%s%s" % (word, pos and "(" + pos + ")", meaning and " " + meaning))
    if example:
        print("例句:", example)
    print("-" * 48)
    print("方法二·词根词缀记忆法 拆解:")
    if prefix:
        pm = next((p["meaning"] for p in pre_list if p["affix"] == prefix), "")
        print("  前缀: %s → %s" % (prefix, pm))
    else:
        print("  前缀: （未匹配已知前缀）")
    print("  词根: %s → （内部词根查 references/affix.md『常见词根表』，脚本不自动判）" % root)
    if suffix:
        sm = next((s["meaning"] for s in suf_list if s["affix"] == suffix), "")
        print("  后缀: %s → %s" % (suffix, sm))
    else:
        print("  后缀: （未匹配已知后缀）")
    print("  组义: 把『前缀义 + 词根义 + 后缀义』串成中文释义，与实际词义校准。")
    print("  锚定(可选): 用一句平实话把词素义与词义绑住，不引入联想法画面。")
    print("=" * 48)


def ordered_chunks(word, entries):
    """返回单词中命中的片段，按其在单词里出现的先后顺序排列（满足成句结构规则的『顺序锁定』）。"""
    w = word.lower()
    seen = []
    for e in entries:
        ch = e["chunk"].lower()
        if ch and ch in w:
            seen.append((w.find(ch), e))
    seen.sort(key=lambda x: x[0])
    return [e for _, e in seen]


def main():
    ap = argparse.ArgumentParser(description="单词记忆机械辅助：切分 + 译码候选")
    ap.add_argument("word", help="英文单词")
    ap.add_argument("--meaning", default="", help="中文释义")
    ap.add_argument("--pos", default="", help="词性")
    ap.add_argument("--example", default="", help="例句")
    ap.add_argument("--mode", default="assoc", choices=["assoc", "affix"],
                   help="assoc=联想记忆法(七步框架，默认)；affix=词根词缀记忆法(方法二)")
    args = ap.parse_args()

    entries, encoding, affix, pinyin = load_map()

    if args.mode == "affix":
        print_affix(args.word, affix, args.meaning, args.pos, args.example)
        return
    word = args.word
    hits = find_chunks(word, entries)

    print("=" * 48)
    print("【%s】%s%s" % (word, args.pos and "(" + args.pos + ")", args.meaning and " " + args.meaning))
    if args.example:
        print("例句:", args.example)
    print("-" * 48)

    print("步骤1 切分候选:")
    if hits:
        for h in hits:
            print("  · 片段 '%s'  →  %s [%s]  (例: %s)" % (
                h["chunk"], "/".join(h["hanzi"]), h["method"], h["eg"]))
    else:
        print("  · 未在映射库命中，请人工按音节/熟词切分（如 earthquake→earth+quake）。")

    print("\n步骤2 译码候选（四法皆可混用、按记忆友好度排序；编码非默认）:")
    for h in sorted(hits, key=lambda e: METHOD_ORDER.get(e["method"], 9)):
        print("  [%s] %s(%s) → %s" % (h["method"], h["chunk"], h["py"], "/".join(h["hanzi"])))

    print("\n步骤3b 编码意象候选（固定编码表；仅四法之一、非默认，勿逐字母拆）:")
    enc = encode_word(word, encoding)
    if enc:
        for seg, img in enc:
            print("  · %s → %s" % (seg, img))
        pieces = " + ".join("%s(%s)" % (img, seg) for seg, img in enc)
        print("  意象序列: %s" % pieces)
        print("  提醒: 编码法只是四法之一、非默认。优先用熟词/拼音把大块并成好记中文；仅当某段熟词/拼音都无好解时才用这些意象，不要为用编码而逐字母拆——模块越少越好。串联句词义须融进剧情（不得贴标签）。")
    else:
        print("  · （单词为空）")

    print("\n步骤3c 双写字母段候选（拼音首字母 vs 编码复数，按句中角色二选一）:")
    doubles = double_letter_candidates(word, pinyin, encoding)
    if doubles:
        for pair, py, enc in doubles:
            if py:
                print("  · %s → %s（拼音首字母·%s）" % (pair, py["cn"], py["type"]))
            else:
                print("  · %s → （拼音首字母表未收录）" % pair)
            print("     或 %s → 两个%s（编码复数，与单字母表一致；量词按物选：两条海马/两把伞）" % (pair, enc))
        print("  选型: 段位要『动』（追/喊/抱/拿）用人物/动物词；当道具（扁担/掩体）用编码复数；画面质量相当时优先编码复数（零新增记忆）。双写字母必须各有去处或合并为一段——先过『拼接核对』。")
    else:
        print("  · （无双写字母段）")

    print("\n步骤4 碎片意象（每段一个荒诞镜头，只备料不成句）:")
    if hits:
        for h in hits:
            print("  · '%s' → %s ：造一个不合常理的画面" % (h["chunk"], "/".join(h["hanzi"])))
    else:
        print("  · （先完成切分/译码，再给每段造意象）")

    print("\n步骤5 ★ 串联成句（越有趣/越通感(刺激·恐怖)越好记，必须出现词义）:")
    ord_hits = ordered_chunks(word, entries)
    if ord_hits:
        pieces = " + ".join("/".join(h["hanzi"]) for h in ord_hits)
        meaning = args.meaning or "（填释义）"
        print("  原序模块: %s  （★字母顺序锁定，不得打乱）" % pieces)
        print("  词义三向嵌入（以「%s」为例，须融进剧情而非贴标签）:" % meaning)
        print("    前置(背景): 「%s驾着%s…」" % (meaning, pieces))
        print("    中插(动作一环): 「%s载着%s…」（词义成动词合理成分，最融合）" % (pieces.split(" + ")[0], meaning))
        print("    后置(收尾,偏弱): 「%s——这就是%s。」（仅无融合点时才用）" % (pieces, meaning))
        print("  写法: 先产出几版，按『中文逻辑+词义融合度』筛掉贴标/拗口版，再从通过的里挑最有趣/最通感那句。")
        print("  例: machine → \"妈妈(ma)把下巴(chin)塞进机器(machine)，被饿(e)疯的鹅咬碎，血溅满脸。\"")
    else:
        print("  （先完成切分/译码，再按原序焊成一句）")

    print("\n步骤6 复习: 当天 / 隔天 / 每周")
    print("步骤7 归纳: 若属同族词，按词根/前后缀归并；特殊词用『找特点』。")
    print("=" * 48)


if __name__ == "__main__":
    main()

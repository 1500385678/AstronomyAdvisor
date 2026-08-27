#!/usr/bin/env python3
"""
md_to_astro_db.py
=================

Phase 0 步骤 0.1:把张勇已有的两篇"自由文本"md 抽成结构化 JSON。

输入:
  - ../../02_天文分支与特点/02_天文分支与特点.md   (天文分支清单)
  - ../../04_天文故事与传说/04_天文故事与传说.md   (经典故事 / 天文传说)
  - ../../06_天文大师与学者/06_天文大师与学者.md   (天文学家与学者)

输出:
  - data/astro_entities.json   (顶层数组,每项一个实体)

抽取策略(启发式,不做 LLM):
  1. md 表格遍历(识别 "## " 段内的 |...| 块)
  2. 02 文件:按表头"核心分支 / 按研究对象 / 速查 / 核心领域"分类,每行 = 一个 branch 实体
  3. 04 文件:抽"经典天文故事"与"天文传说"两张表,跳过"大师名言"表(与 06 重复)
  4. 06 文件:解析 "## X、{姓名}:{头衔}" 段,提取生卒、国籍、核心思想表
  5. 06 文件:另抽"大师代表作"表(代表作回填)与"天文大师名言"表(quote 实体)

不做:
  - 不抓 88 星座 / HYG 星表(留给 Phase 0 后续步骤)
  - 不入库 SQLite(只产 JSON,留给下一阶段)
  - 不做翻译(中英名常量表只覆盖已知几个,缺失留空,后续手补)

使用:
  python scripts/md_to_astro_db.py --out data/astro_entities.json
  python scripts/md_to_astro_db.py --source-root /path/to/_AstronomyLib
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 路径与常量
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
# scripts/ -> AstronomyWeb/ -> _AstronomyLib/ -> 35-天文-Astronomy/
LIB_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_SOURCE_ROOT = LIB_ROOT

SOURCE_02_REL = "02_天文分支与特点/02_天文分支与特点.md"
SOURCE_04_REL = "04_天文故事与传说/04_天文故事与传说.md"
SOURCE_06_REL = "06_天文大师与学者/06_天文大师与学者.md"

# 中英名常量(覆盖 02 + 06 中出现的几个高频名,缺失留空,后续手补)
NAME_EN: dict[str, str] = {
    # 分支
    "天体物理学": "Astrophysics",
    "天体力学": "Celestial Mechanics",
    "天体化学": "Astrochemistry",
    "宇宙学": "Cosmology",
    "太阳物理学": "Solar Physics",
    "行星科学": "Planetary Science",
    "恒星天文学": "Stellar Astronomy",
    "星系天文学": "Galactic Astronomy",
    # 大师
    "哥白尼": "Copernicus",
    "伽利略": "Galileo",
    "牛顿": "Newton",
    "爱因斯坦": "Einstein",
}

# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------

_PUNCT_STRIP = re.compile(r"[、，。；:""''《》()()【】\[\]·.\-—_,/\\:;!?！？]")


def slugify_zh(s: str) -> str:
    """中文/混合名 → 稳定 ID 段(只去标点,保留中文)。"""
    s = (s or "").strip()
    s = _PUNCT_STRIP.sub("", s)
    return s or "x"


def parse_md_tables(md_text: str):
    """Yields (header: list[str], rows: list[list[str]])。

    规则:连续以 '|' 开头的行,第二行形如 '| --- | --- |' 即表格头。"""
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if (
            line.lstrip().startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|[\s\-:|]+\|\s*$", lines[i + 1])
        ):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            data: list[list[str]] = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                data.append(row)
                i += 1
            yield header, data
        else:
            i += 1


# ---------------------------------------------------------------------------
# 02:天文分支
# ---------------------------------------------------------------------------


# 段内 `**分类名**:` 标记 → category 映射(启发式,按出现顺序就近匹配)
_CATEGORY_MARKERS = [
    ("核心分支", "核心分支"),
    ("按研究对象", "按研究对象"),
    ("核心领域", "核心领域"),
    ("速查", "速查"),
]


def _detect_category(text: str, table_pos: int) -> str:
    """在 table 之前最近的"**关键词**："标记决定分类。

    修复:旧版用迭代式两两比较,会因 last_cat 起始为"未分类"导致 cur_idx=-1,
    进而使首次找到的 marker 永远胜出,后续段全部归到"核心分支"。
    正确做法:扫所有 marker,取离 table 最近的(位置最大)那一个。
    """
    prefix = text[:table_pos]
    best_pos = -1
    best_cat = "未分类"
    for marker, cat in _CATEGORY_MARKERS:
        idx = prefix.rfind(f"**{marker}**")
        if idx >= 0 and idx > best_pos:
            best_pos = idx
            best_cat = cat
    return best_cat


def extract_branches(md_text: str, source_file: str) -> list[dict]:
    entities: list[dict] = []
    seen: set[str] = set()

    # 按 h2 段遍历:每段内再找表格,category 由段内"**Xxx**："标记决定
    sections = re.split(r"^## ", md_text, flags=re.MULTILINE)
    for sec in sections[1:]:
        sec_with_h2 = "## " + sec  # 便于 offset 计算
        for header, rows in parse_md_tables(sec):
            # 跳过名言表(06 才会出现,02 不会;保险起见做一次过滤)
            if any("名言" in h for h in header):
                continue
            # 找当前表在段内的位置:
            # 不能用 "|".join(header) —— 实际表格行是 "| 分支 | 说明 |" 含空格
            # 用正则匹配 "| 分支 | 说明 | ..." 容许空格
            header_pat = r"\|\s*" + r"\s*\|\s*".join(re.escape(h) for h in header) + r"\s*\|"
            m = re.search(header_pat, sec_with_h2)
            table_pos = m.start() if m else 0
            category = _detect_category(sec_with_h2, table_pos)
            # 速查表与"核心领域"在 02 末尾并列,标记会重叠 → 靠"速查"段标题里"**速查**"就近匹配
            for row in rows:
                if not row or not row[0]:
                    continue
                name = row[0]
                if name in ("分支", "领域", "思想", "大师", "名", "核心分支", "按研究对象分的分支"):
                    continue
                desc = row[1] if len(row) > 1 else ""
                representative = row[2] if len(row) > 2 else ""
                eid = f"branch-{slugify_zh(name)}"
                if eid in seen:
                    continue
                seen.add(eid)
                entities.append(
                    {
                        "id": eid,
                        "type": "branch",
                        "name_cn": name,
                        "name_en": NAME_EN.get(name, ""),
                        "description": desc,
                        "category": category,
                        "representative": representative,
                        "source_file": source_file,
                    }
                )
    return entities


# ---------------------------------------------------------------------------
# 04:天文故事与传说
# ---------------------------------------------------------------------------


# 04 表头 → (实体类型前缀, category 中文) 的映射
# "大师名言"表跳过:与 06 重复,避免 quote 实体重复入库
_STORY_TABLE_RULES = [
    (("故事",), "story", "经典故事"),
    (("传说",), "legend", "天文传说"),
]


def _classify_story_table(header: list[str]) -> tuple[str, str] | None:
    """根据表头判断是否要抽、并决定 type 前缀 + category。

    优先级:出现"故事" → 故事;出现"传说" → 传说;出现"名言" → 跳过(None)。
    """
    if any("名言" in h for h in header):
        return None
    for keys, type_prefix, cat in _STORY_TABLE_RULES:
        if any(any(k in h for k in keys) for h in header):
            return type_prefix, cat
    return None


def extract_stories_legends(md_text: str, source_file: str) -> list[dict]:
    """从 04 文件抽"经典天文故事"与"天文传说"两表,每行 = 一个实体。

    字段:type=story | legend, name_cn, category, insight, 其它空值。
    名言表直接跳过(与 06 quote 重复)。
    """
    entities: list[dict] = []
    seen: set[str] = set()

    for header, rows in parse_md_tables(md_text):
        rule = _classify_story_table(header)
        if rule is None:
            continue
        type_prefix, category = rule
        for r in rows:
            if not r or not r[0]:
                continue
            # 跳表头行(在数据中残留"故事"或"传说"作为列名)
            if r[0] in ("故事", "传说", "经典天文故事", "天文传说", "名", "大师"):
                continue
            eid = f"{type_prefix}-{slugify_zh(r[0])}"
            if eid in seen:
                continue
            seen.add(eid)
            entities.append(
                {
                    "id": eid,
                    "type": type_prefix,
                    "name_cn": r[0].strip(),
                    "name_en": "",
                    "category": category,
                    "insight": r[1].strip() if len(r) > 1 and r[1] else "",
                    "description": "",
                    "source_file": source_file,
                }
            )
    return entities


# ---------------------------------------------------------------------------
# 06:天文大师与学者
# ---------------------------------------------------------------------------


def extract_masters(md_text: str, source_file: str) -> list[dict]:
    entities: list[dict] = []
    seen: set[str] = set()

    # 1) 从每个 h2 / h3 段抽大师档案
    #    兼容 06 文件"一、天文大师讲大师"内部的 ### 哥白尼(等)h3 段
    sections = re.split(r"^##+ ", md_text, flags=re.MULTILINE)
    for sec in sections[1:]:
        first_line = sec.splitlines()[0].strip()
        # h2 形如 "二、伽利略：望远镜天文观测奠基者"
        m = re.match(r"^[一二三四五六七八九十]+、(.{2,8})[：:](.*)$", first_line)
        # h3 形如 "哥白尼：日心说开创者"(无序号前缀)
        if not m:
            m = re.match(r"^(?!#)(.{2,8})[：:](.*)$", first_line)
        if not m:
            continue
        name = m.group(1).strip()
        title_desc = m.group(2).strip()

        # 生卒(支持中文括号与英文括号,支持 "年-年" / "年—年")
        bio = re.search(r"[（(](\d{3,4})年[-—](\d{3,4})年[）)]", sec)
        birth = int(bio.group(1)) if bio else None
        death = int(bio.group(2)) if bio else None
        lifespan = f"{birth}-{death}" if birth and death else ""

        # 国籍(取"伟大/著名"前的中文短语,例 "波兰伟大天文学家",
        # 或 "波兰**伟大天文学家" 中间含 markdown 加粗 ** 也算)
        nat = re.search(
            r"([\u4e00-\u9fa5]{1,6}?)\**?(伟大|著名|知名)",
            sec,
        )
        nationality = nat.group(1) if nat else ""

        # 核心思想表
        key_thoughts: list[dict] = []
        for header, rows in parse_md_tables(sec):
            if any("思想" in h for h in header) and len(header) >= 2:
                for r in rows:
                    if r and r[0] and r[0] != "思想":
                        key_thoughts.append(
                            {
                                "thought": r[0],
                                "explain": r[1] if len(r) > 1 else "",
                            }
                        )

        eid = f"master-{slugify_zh(name)}"
        if eid in seen:
            continue
        seen.add(eid)
        entities.append(
            {
                "id": eid,
                "type": "master",
                "name_cn": name,
                "name_en": NAME_EN.get(name, ""),
                "title": title_desc,
                "nationality": nationality,
                "birth_year": birth,
                "death_year": death,
                "lifespan": lifespan,
                "key_thoughts": key_thoughts,
                "key_works": [],
                "source_file": source_file,
                "section": first_line,
            }
        )

    # 2) 用"大师代表作"表回填 key_works / title
    for header, rows in parse_md_tables(md_text):
        if not any("代表作" in h for h in header):
            continue
        for r in rows:
            if not r or not r[0] or r[0] == "大师":
                continue
            eid = f"master-{slugify_zh(r[0])}"
            for e in entities:
                if e["id"] == eid:
                    e["key_works"] = [r[2]] if len(r) > 2 and r[2] else e["key_works"]
                    if not e.get("title") and len(r) > 1 and r[1]:
                        e["title"] = r[1]
                    break

    # 3) 名言表
    for header, rows in parse_md_tables(md_text):
        if not any("名言" in h for h in header):
            continue
        for r in rows:
            if not r or not r[0] or r[0] == "大师":
                continue
            entities.append(
                {
                    "id": f"quote-{slugify_zh(r[0])}",
                    "type": "quote",
                    "name_cn": r[0],
                    "text": r[1] if len(r) > 1 else "",
                    "source_file": source_file,
                }
            )

    return entities


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(
        description="把 02/06 自由文本 md 抽成 astro_entities.json"
    )
    p.add_argument(
        "--out",
        default=str(SCRIPT_DIR.parent / "data" / "astro_entities.json"),
        help="输出 JSON 路径",
    )
    p.add_argument(
        "--source-root",
        default=str(DEFAULT_SOURCE_ROOT),
        help="_AstronomyLib 根目录(默认按脚本位置推断)",
    )
    args = p.parse_args()

    src02 = Path(args.source_root) / SOURCE_02_REL
    src04 = Path(args.source_root) / SOURCE_04_REL
    src06 = Path(args.source_root) / SOURCE_06_REL
    if not src02.exists():
        print(f"[ERR] 缺源文件: {src02}", file=sys.stderr)
        return 2
    if not src04.exists():
        print(f"[ERR] 缺源文件: {src04}", file=sys.stderr)
        return 2
    if not src06.exists():
        print(f"[ERR] 缺源文件: {src06}", file=sys.stderr)
        return 2

    md02 = src02.read_text(encoding="utf-8")
    md04 = src04.read_text(encoding="utf-8")
    md06 = src06.read_text(encoding="utf-8")

    entities: list[dict] = []
    entities.extend(extract_branches(md02, SOURCE_02_REL))
    entities.extend(extract_stories_legends(md04, SOURCE_04_REL))
    entities.extend(extract_masters(md06, SOURCE_06_REL))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(entities, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # 控制台摘要
    by_type: dict[str, int] = {}
    for e in entities:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print(
        f"[OK] {out_path}  total={len(entities)}  by_type={by_type}  "
        f"source_root={args.source_root}"
    )

    # 验收:条目数 ≥ 10
    return 0 if len(entities) >= 10 else 3


if __name__ == "__main__":
    sys.exit(main())

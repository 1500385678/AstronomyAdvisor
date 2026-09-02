"""
merge_constellations_seed · Phase 0 #2 步 3 · 合并 88 星座种子到主 JSON
==========================================================================

背景:
- 0902 立 `data/constellations_seed.json`(9 条:猎户 / 大熊 / 小熊 / 天蝎 /
  狮子 / 天鹅 / 天琴 / 仙后 / 半人马,首批破零样本)
- 同时具备 schema(`data/astro_entities.schema.md` constellation 字段,0902 闭项)
- 主 JSON `data/astro_entities.json` 当时未合并(避免污染抽取脚本回归)
- 本步(#2 步 3)正式合并,按 schema 要求补 `source_file` 字段

不做的:
- 不改 `constellations_seed.json` 内容(权威数据,只读)
- 不动 schema 文档(已 0902 闭项)
- 不扩到 88 条(NW/N4/N1 批次扩到 27 条留待 0904+ 后续,避免单 commit 步子过大)
- 不抽新数据(只搬运,沙箱式合并)
- 不动 merge_planets_seed.py(已 0901 闭项)

使用:
    python3 scripts/merge_constellations_seed.py
    # 打印:before / after / by_type diff / added 列表
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
MAIN_JSON = ROOT / "data" / "astro_entities.json"
SEED_JSON = ROOT / "data" / "constellations_seed.json"
SEED_LABEL = "data/constellations_seed.json"


def main() -> int:
    if not SEED_JSON.exists():
        print(f"[err] 星座种子缺失: {SEED_JSON}", file=sys.stderr)
        return 1
    seed = json.loads(SEED_JSON.read_text(encoding="utf-8"))
    ents = json.loads(MAIN_JSON.read_text(encoding="utf-8"))

    before_total = len(ents)
    before_types = dict(Counter(e.get("type") for e in ents))

    existing_ids = {e.get("id") for e in ents}
    added, skipped = [], []
    for c in seed:
        cid = c.get("id")
        if cid in existing_ids:
            skipped.append(cid)
            continue
        # 按 schema 要求补 source_file
        c["source_file"] = SEED_LABEL
        ents.append(c)
        added.append(cid)

    after_total = len(ents)
    after_types = dict(Counter(e.get("type") for e in ents))

    MAIN_JSON.write_text(
        json.dumps(ents, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[ok] 合并完成")
    print(f"  before: total={before_total}, by_type={before_types}")
    print(f"  after:  total={after_total}, by_type={after_types}")
    print(f"  added:  {len(added)} ({', '.join(added)})")
    if skipped:
        print(f"  skipped(已存在): {len(skipped)} ({', '.join(skipped)})")
    print(f"  constellation diff: {before_types.get('constellation', 0)} → {after_types.get('constellation', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

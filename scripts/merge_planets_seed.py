"""
merge_planets_seed · Phase 0 #4 步 5 · 合并行星种子到主 JSON
================================================================

背景:
- 0829 立 `data/planets_seed.json`(9 条:8 大行星 + 冥王星矮行星)
- 同时立 schema(`data/astro_entities.schema.md` planet 字段)
- 主 JSON `data/astro_entities.json` 当时未合并(避免污染抽取脚本回归)
- 本步(#4 步 5)正式合并,按 schema 要求补 `source_file` 字段

不做的:
- 不改 `planets_seed.json` 内容(权威数据,只读)
- 不动 schema 文档(已 0829 闭项)
- 不合并 deep_sky(深空种子未就绪,待 #4 步 4 完成后)
- 不抽新数据(只搬运)

使用:
    python3 scripts/merge_planets_seed.py
    # 打印:total before / after / by_type diff
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
MAIN_JSON = ROOT / "data" / "astro_entities.json"
SEED_JSON = ROOT / "data" / "planets_seed.json"
SEED_LABEL = "data/planets_seed.json"


def main() -> int:
    if not SEED_JSON.exists():
        print(f"[err] 行星种子缺失: {SEED_JSON}", file=sys.stderr)
        return 1
    seed = json.loads(SEED_JSON.read_text(encoding="utf-8"))
    ents = json.loads(MAIN_JSON.read_text(encoding="utf-8"))

    before_total = len(ents)
    before_types = dict(Counter(e.get("type") for e in ents))

    existing_ids = {e.get("id") for e in ents}
    added, skipped = [], []
    for p in seed:
        pid = p.get("id")
        if pid in existing_ids:
            skipped.append(pid)
            continue
        # 按 schema 要求补 source_file
        p["source_file"] = SEED_LABEL
        ents.append(p)
        added.append(pid)

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
    print(f"  planet diff: {before_types.get('planet', 0)} → {after_types.get('planet', 0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

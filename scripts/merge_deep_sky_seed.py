"""
merge_deep_sky_seed · Phase 0 #4 步 5 · 合并 Messier 6 条 sample 到主 JSON
==========================================================================

背景:
- 0905 T1 立 `data/deep_sky_seed.json`(6 条:M1 蟹状星云 / M31 仙女座星系 /
  M42 猎户大星云 / M45 昴星团 / M51 涡状星系 / M57 环状星云,4 object_type 全集
  覆盖:超新星遗迹 1 / 星系 2 / 星云 2 / 星团 1)
- 0905 .plan 第 12/42 行明文"本步只立不合并(留合并给 0906 节奏)",本步兑现
- 0903 立的 `merge_constellations_seed.py` 范式是"先 seed 后合"两步走,本步
  复制范式(读 / by_id 跳过 / 补 source_file / 写回 / 打印 diff)
- 0905 立 seed 时 M45 object_type 简写为 `星团`,schema 第 160 行枚举要求
  `星团(球状/疏散)`,Pleiades 是疏散星团,本合并器规范化 `星团` → `星团(疏散)`
  (seed 文件原样保留作为权威源不动,规范化仅对写入主 JSON 的副本生效)

不做的:
- 不改 `deep_sky_seed.json` 内容(权威数据,只读)
- 不动 schema 文档(0829 立,本步只动主 JSON)
- 不扩到 12 条(0906 巡检第 42 行建议,本步只合 6 不扩 6,扩 6 留 0907+ 节奏)
- 不抽新数据(只搬运,沙箱式合并)
- 不动 merge_planets_seed.py / merge_constellations_seed.py(0901 / 0903 闭项)
- 不动 backend main.py(0905 巡检 #5 项 0 增量挂账,本步 0 端点新增)

使用:
    python3 scripts/merge_deep_sky_seed.py
    # 打印:before / after / by_type diff / added 列表 / M45 规范化说明
    # 二次跑 idempotent:6 个 dso-m* 全 skipped,67 条不变
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
MAIN_JSON = ROOT / "data" / "astro_entities.json"
SEED_JSON = ROOT / "data" / "deep_sky_seed.json"
SEED_LABEL = "data/deep_sky_seed.json"

# schema 0829 §deep_sky_object object_type 枚举:星系 / 星云 / 星团(球状/疏散) / 超新星遗迹
# 0905 立 seed 时 M45 简写为 `星团`,合并时按 Pleiades 类型学规范化
_OBJECT_TYPE_NORMALIZE = {
    "星团": "星团(疏散)",  # M45 Pleiades 疏散星团
}


def _normalize(dso: dict) -> tuple[dict, list[str]]:
    """合并时规范化 dso 副本(不动 seed)。返回 (副本, 修正说明列表)。"""
    fixes: list[str] = []
    obj_type = dso.get("object_type", "")
    if obj_type in _OBJECT_TYPE_NORMALIZE:
        new_type = _OBJECT_TYPE_NORMALIZE[obj_type]
        fixes.append(f"object_type: {obj_type!r} → {new_type!r}")
        dso = dict(dso)
        dso["object_type"] = new_type
    return dso, fixes


def main() -> int:
    if not SEED_JSON.exists():
        print(f"[err] 深空种子缺失: {SEED_JSON}", file=sys.stderr)
        return 1
    seed = json.loads(SEED_JSON.read_text(encoding="utf-8"))
    ents = json.loads(MAIN_JSON.read_text(encoding="utf-8"))

    before_total = len(ents)
    before_types = dict(Counter(e.get("type") for e in ents))

    existing_ids = {e.get("id") for e in ents}
    added, skipped, fixes_log = [], [], []
    for dso in seed:
        did = dso.get("id")
        if did in existing_ids:
            skipped.append(did)
            continue
        dso_norm, fixes = _normalize(dso)
        if fixes:
            fixes_log.append(f"{did}: " + "; ".join(fixes))
        # 按 schema 要求补 source_file
        dso_norm["source_file"] = SEED_LABEL
        ents.append(dso_norm)
        added.append(did)

    after_total = len(ents)
    after_types = dict(Counter(e.get("type") for e in ents))

    MAIN_JSON.write_text(
        json.dumps(ents, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("[ok] 深空合并完成")
    print(f"  before: total={before_total}, by_type={before_types}")
    print(f"  after:  total={after_total}, by_type={after_types}")
    print(f"  added:  {len(added)} ({', '.join(added)})")
    if skipped:
        print(f"  skipped(已存在): {len(skipped)} ({', '.join(skipped)})")
    print(
        f"  deep_sky_object diff: {before_types.get('deep_sky_object', 0)} → "
        f"{after_types.get('deep_sky_object', 0)}"
    )
    if fixes_log:
        print("  规范化修正:")
        for line in fixes_log:
            print(f"    - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

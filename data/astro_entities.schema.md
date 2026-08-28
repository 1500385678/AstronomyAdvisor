# astro_entities.json · 字段约定

> Phase 0 · 步骤 0.1 产物的 schema 文档
> 配套脚本:`scripts/md_to_astro_db.py`
> 输出文件:`data/astro_entities.json`(顶层数组,每项一个实体)
> 种子数据:`data/planets_seed.json`(Phase 0 #4 · 8 大行星权威数据,20260829 立)

## 顶层结构

`astro_entities.json` 是一个 **JSON 数组**,每个元素是一个 entity 对象。**不放外层 metadata**,保持 Phase 0 后续步骤(数据库 / 向量库)接入时扁平化。

```json
[
  { ...entity1 },
  { ...entity2 }
]
```

## entity.type 枚举

| type | 含义 | 来源 md | 计数目标(初始) |
|------|------|---------|----------------|
| `branch` | 天文分支(天体物理 / 天体力学 / 宇宙学 …) | `02_天文分支与特点.md` | ≥ 12(覆盖核心分支 + 按研究对象 + 速查) |
| `story` | 经典天文故事(哥白尼与日心说 / 伽利略与望远镜 …) | `04_天文故事与传说.md` | ≥ 2(当前 2 条,后续可补) |
| `legend` | 天文传说(牛郎织女 / 嫦娥奔月 …) | `04_天文故事与传说.md` | ≥ 2(当前 2 条,后续可补) |
| `master` | 天文大师/学者(哥白尼 / 伽利略 / 牛顿 / 爱因斯坦 …) | `06_天文大师与学者.md` | ≥ 4(目前 4 位大师,后续手补 6 位以上) |
| `quote` | 大师名言 | `06_天文大师与学者.md` | ≥ 4 |
| `constellation` | 88 星座档案(中英文 + 神话 + 主要恒星) | 待编纂(Phase 0 #2) | ≥ 88 |
| `star` | 亮星(HYG 数据库 100-200 颗) | HYG 公开数据集(Phase 0 #3) | ≥ 100 |
| `planet` | 8 大行星 | NASA 公开数据(Phase 0 #4 种子) | 8 |
| `deep_sky_object` | 重要深空天体(梅西耶 50+) | Messier 目录(Phase 0 #4) | ≥ 50 |

## branch 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `branch-{slug}` · slug = 去除标点的中文名(去重后稳定) |
| `type` | string | ✓ | 固定 `"branch"` |
| `name_cn` | string | ✓ | 中文名(从表格第一列取) |
| `name_en` | string | - | 英文名;常量表里命中就填,缺则空串(后续手补) |
| `description` | string | ✓ | 一句话定义(表格第二列) |
| `category` | string | ✓ | 分类:`核心分支` / `按研究对象` / `速查` / `核心领域` |
| `representative` | string | - | 代表方向(表格第三列,仅 02 速查表有) |
| `source_file` | string | ✓ | 相对 `_AstronomyLib/` 的源 md 路径 |

## master 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `master-{slug}` |
| `type` | string | ✓ | 固定 `"master"` |
| `name_cn` | string | ✓ | 中文姓名 |
| `name_en` | string | - | 英文名(常量表) |
| `title` | string | ✓ | 头衔/地位,例 "日心说开创者" |
| `nationality` | string | - | 国籍,启发式抽取(取"伟大/著名"前的中文短语) |
| `birth_year` | int | - | 出生年,缺则 null |
| `death_year` | int | - | 去世年,缺则 null |
| `lifespan` | string | - | `"YYYY-YYYY"`,缺则空串 |
| `key_thoughts` | list[object] | - | 核心思想,每项 `{"thought": ..., "explain": ...}` |
| `key_works` | list[string] | - | 代表作(从"大师代表作"表回填,缺则空数组) |
| `source_file` | string | ✓ | 源 md 相对路径 |
| `section` | string | - | 所在 h2 段标题(便于溯源) |

## quote 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `quote-{slug}` |
| `type` | string | ✓ | 固定 `"quote"` |
| `name_cn` | string | ✓ | 大师中文名(可与 master.id 弱关联) |
| `text` | string | ✓ | 名言正文 |
| `source_file` | string | ✓ | 源 md 相对路径 |

## story 字段(经典天文故事)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `story-{slug}` |
| `type` | string | ✓ | 固定 `"story"` |
| `name_cn` | string | ✓ | 故事名(例 "哥白尼与日心说") |
| `name_en` | string | - | 英文名;常量表缺则空串 |
| `category` | string | ✓ | 固定 `"经典故事"` |
| `insight` | string | - | 一句话启示;表格"启示"列,缺则空串 |
| `description` | string | - | 故事正文;当前抽取仅取表行,后续可补 |
| `source_file` | string | ✓ | 源 md 相对路径,固定 `04_天文故事与传说/04_天文故事与传说.md` |

## legend 字段(天文传说)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `legend-{slug}` |
| `type` | string | ✓ | 固定 `"legend"` |
| `name_cn` | string | ✓ | 传说名(例 "牛郎织女") |
| `name_en` | string | - | 英文名;缺则空串 |
| `category` | string | ✓ | 固定 `"天文传说"` |
| `insight` | string | - | 一句话启示;表格"启示"列,缺则空串 |
| `description` | string | - | 传说正文;当前抽取仅取表行,后续可补 |
| `source_file` | string | ✓ | 源 md 相对路径,固定 `04_天文故事与传说/04_天文故事与传说.md` |

## constellation 字段(88 星座档案 · Phase 0 #2)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `constellation-{iau_abbr_lowercase}` 例 `constellation-ori` (猎户座) |
| `type` | string | ✓ | 固定 `"constellation"` |
| `name_cn` | string | ✓ | 中文名(如 "猎户座") |
| `name_en` | string | ✓ | 英文名(如 "Orion") |
| `name_latin` | string | ✓ | 拉丁名(学名,如 "Orion") |
| `iau_abbr` | string | ✓ | IAU 3 字母缩略(大写,如 "Ori") |
| `hemisphere` | string | ✓ | `北` / `南` / `跨` |
| `best_season` | string | ✓ | `春` / `夏` / `秋` / `冬` |
| `area_sq_deg` | number | - | 面积(平方度) |
| `main_stars` | list[string] | - | 主要恒星名(如 `["参宿四", "参宿七"]`) |
| `mythology` | string | - | 神话背景(希腊 / 中国 / 其他) |
| `source_file` | string | - | 来源 md;Phase 0 #2 起步阶段可空,后续补 |

## star 字段(亮星 · Phase 0 #3)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `star-{hip_number}` 例 `star-32349` (天狼星 Sirius) |
| `type` | string | ✓ | 固定 `"star"` |
| `name_cn` | string | - | 中文常用名(如 "天狼星");常量表命中填,缺则空串 |
| `name_en` | string | - | 英文常用名(如 "Sirius") |
| `hip_number` | int | ✓ | Hipparcos 编号(HYG 主键) |
| `ra_h` | number | ✓ | 赤经(小时,0-24) |
| `dec_deg` | number | ✓ | 赤纬(度,-90 ~ +90) |
| `magnitude` | number | ✓ | 视星等(越小越亮,负数极亮) |
| `spectral_type` | string | - | 光谱型(如 "A1V") |
| `distance_ly` | number | - | 距离(光年) |
| `constellation_abbr` | string | - | 所属星座 IAU 缩略(如 "CMa" 大犬座) |
| `source_file` | string | - | 来源;HYG 公开数据集可不填 |

## planet 字段(8 大行星 · Phase 0 #4)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `planet-{name_en_lowercase}` 例 `planet-jupiter` |
| `type` | string | ✓ | 固定 `"planet"` |
| `name_cn` | string | ✓ | 中文名(如 "木星") |
| `name_en` | string | ✓ | 英文名(如 "Jupiter") |
| `is_dwarf` | bool | ✓ | 是否矮行星(如冥王星);`false` 为主行星 |
| `order_from_sun` | int | ✓ | 距太阳序数(水星=1 … 海王星=8) |
| `orbital_period_days` | number | ✓ | 公转周期(地球日;木星等用 365.25 * 年数) |
| `diameter_km` | number | ✓ | 直径(km) |
| `mass_kg` | number | ✓ | 质量(kg,科学计数,如 `1.898e27`) |
| `moons_count` | int | ✓ | 已确认卫星数(数据按 NASA Planetary Fact Sheet 2024+ 更新) |
| `mythology` | string | - | 神话背景(罗马 / 希腊 / 其他) |
| `source_file` | string | - | 种子阶段可不填,Phase 0 #4 正式合并时填 `data/planets_seed.json` |

## deep_sky_object 字段(深空天体 · Phase 0 #4)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | ✓ | `dso-{catalog_id_lowercase}` 例 `dso-m31`,`dso-ngc-224` |
| `type` | string | ✓ | 固定 `"deep_sky_object"` |
| `catalog_id` | string | ✓ | 目录编号(如 "M31" / "NGC 224") |
| `name_cn` | string | - | 中文常用名(如 "仙女座星系") |
| `name_en` | string | ✓ | 英文名(如 "Andromeda Galaxy") |
| `object_type` | string | ✓ | `星系` / `星云` / `星团`(球状/疏散) / `超新星遗迹` |
| `ra_h` | number | ✓ | 赤经(小时) |
| `dec_deg` | number | ✓ | 赤纬(度) |
| `magnitude` | number | - | 视星等 |
| `constellation_abbr` | string | - | 所属星座 IAU 缩略 |
| `description` | string | - | 一句话简介 |
| `source_file` | string | - | Messier / NGC 公开目录;可不填 |

## 字段约定(全局)

- **id 稳定性**:用 `slug` 拼前缀,确保同一来源产出同一 id;抽取脚本重跑后,下游使用方可按 id diff / merge。
- **空值**:可选字段缺数据时,字符串写 `""`,数值写 `null`,列表写 `[]`,**不省略键**(便于 schema 校验)。
- **多源冲突**:同一名字在不同表里出现(02 速查表 + 02 核心分支表),取**首次出现**的 `category`,其余表行跳过(`seen` 集合去重)。
- **不做翻译**:仅常量表里几个高频名有 `name_en`,其余留空,后续步骤(Phase 0 #3 88 星座)统一翻译。

## 下游使用建议

1. **Phase 0 #2 #3** 用本 JSON 作为输入,直接转 SQLite `constellations` / `stars` 表的种子数据。
2. **飞书 Bot 速查** 把 `branch` 列表 + `master` 列表打包进 LLM 上下文,作为"分支 / 大师"问题的兜底知识。
3. **向量库** (Phase 2 引入) 用 `description + key_thoughts` 拼成 `entity.text`,灌入 Chroma。

## Phase 0 #2 / #3 / #4 抽取路线图(20260829 立)

| 步骤 | 目标 | 数据源 | 输出文件 | 状态 |
|------|------|--------|---------|------|
| **#2 步 1** | 立 88 星座档案 schema | 本文档(上方 constellation 字段) | — | ✅ 20260829 |
| **#2 步 2** | 手工入 88 星座种子(中英文 + IAU 缩略 + 季节 + 神话) | IAU 星座表 + 中文化翻译 | `data/constellations_seed.json` | 📋 下一步 |
| **#2 步 3** | 接入 `scripts/md_to_astro_db.py` `extract_constellations()` | md 资料(若编纂) | `astro_entities.json` 新增 constellation type | 📋 |
| **#3 步 1** | 立亮星 schema | 本文档(上方 star 字段) | — | ✅ 20260829 |
| **#3 步 2** | 拉 HYG 数据库 v3(CSV 公开) | HYG 官网 csv | `data/stars_hyg.csv` | 📋 |
| **#3 步 3** | 筛 magnitude < 6 + 中文名映射 | HYG + 中文化 | `data/stars_seed.json` | 📋 |
| **#4 步 1** | 立 8 大行星 schema | 本文档(上方 planet 字段) | — | ✅ 20260829 |
| **#4 步 2** | 手工入 8 大行星权威种子 | NASA Planetary Fact Sheet | `data/planets_seed.json` | ✅ 20260829 |
| **#4 步 3** | 抽 1 颗矮行星冥王星(is_dwarf=true)作为 schema 验证 | 同上 | 同上 | ✅ 20260829 |
| **#4 步 4** | 入库 Messier 110 种子(M1-M110) | Messier 公开目录 | `data/deep_sky_seed.json` | 📋 |
| **#4 步 5** | merge 行星/深空种子到 `astro_entities.json` | 种子文件 | `astro_entities.json` | 📋 |

> **设计原则**:**schema 先行,种子入库,合并到主 JSON**。每加一个 type,先在本文档立字段,再立独立种子文件,最后由 `md_to_astro_db.py` 的合并器(或一次性脚本)合到 `astro_entities.json`,便于回滚和 review。

## 验收

- [x] 脚本可单文件运行,无外部依赖(仅 Python 3.10+ 标准库)
- [x] 输出 JSON 数组长度 ≥ 10
- [x] 字段对齐本文档
- [x] 02/04/06 真实条目覆盖,不伪造

<!-- AUTO-GENERATED v0.1 DO-NOT-EDIT-MANUALLY -->

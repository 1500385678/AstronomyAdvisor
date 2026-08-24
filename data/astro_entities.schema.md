# astro_entities.json · 字段约定

> Phase 0 · 步骤 0.1 产物的 schema 文档
> 配套脚本:`scripts/md_to_astro_db.py`
> 输出文件:`data/astro_entities.json`(顶层数组,每项一个实体)

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
| `master` | 天文大师/学者(哥白尼 / 伽利略 / 牛顿 / 爱因斯坦 …) | `06_天文大师与学者.md` | ≥ 4(目前 4 位大师,后续手补 6 位以上) |
| `quote` | 大师名言 | `06_天文大师与学者.md` | ≥ 4 |

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

## 字段约定(全局)

- **id 稳定性**:用 `slug` 拼前缀,确保同一来源产出同一 id;抽取脚本重跑后,下游使用方可按 id diff / merge。
- **空值**:可选字段缺数据时,字符串写 `""`,数值写 `null`,列表写 `[]`,**不省略键**(便于 schema 校验)。
- **多源冲突**:同一名字在不同表里出现(02 速查表 + 02 核心分支表),取**首次出现**的 `category`,其余表行跳过(`seen` 集合去重)。
- **不做翻译**:仅常量表里几个高频名有 `name_en`,其余留空,后续步骤(Phase 0 #3 88 星座)统一翻译。

## 下游使用建议

1. **Phase 0 #2 #3** 用本 JSON 作为输入,直接转 SQLite `constellations` / `stars` 表的种子数据。
2. **飞书 Bot 速查** 把 `branch` 列表 + `master` 列表打包进 LLM 上下文,作为"分支 / 大师"问题的兜底知识。
3. **向量库** (Phase 2 引入) 用 `description + key_thoughts` 拼成 `entity.text`,灌入 Chroma。

## 验收

- [x] 脚本可单文件运行,无外部依赖(仅 Python 3.10+ 标准库)
- [x] 输出 JSON 数组长度 ≥ 10
- [x] 字段对齐本文档
- [x] 02/06 真实条目覆盖,不伪造

<!-- AUTO-GENERATED v0.1 DO-NOT-EDIT-MANUALLY -->

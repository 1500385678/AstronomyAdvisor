# AstronomyAdvisor · Backend

> Phase 1 · W2 Day 1 后端骨架(2026-08-31 立)
> 行业代号:35-天文-Astronomy
> 项目代号:**AstronomyAdvisor**(与 `项目开发计划.md` / GitHub / Gitee 仓库名一致)
> 别名说明:`AstroAdvisor` 是早期内部别名,仅出现在 `天文顾问开发架构与计划.md` 历史草稿,主计划与仓库统一为 `AstronomyAdvisor`

## 一、当前范围

W2 Day 1 仅交付 FastAPI 最小骨架,**不包含**:

- 业务路由(星图 / 事件 / 观测指引 / 天体档案)—— 见 Phase 1 后续项
- 数据库接入(Phase 0 后续会立 SQLite,这里只读 JSON)
- LLM / 历算库 / 鉴权(Phase 1 后段、Phase 2 接入)
- 前端页面骨架(独立 `frontend/` 仓库/目录,W2 后段开)

## 二、目录结构

```
backend/
├── README.md            本文件
├── requirements.txt     FastAPI + uvicorn + pydantic
└── main.py              FastAPI app 入口 + 5 个端点
```

## 三、端点清单

| 方法 | 路径 | 说明 | 标签 |
|------|------|------|------|
| GET | `/` | 项目元信息(无依赖) | meta |
| GET | `/health` | 健康检查 + 数据文件可达性 | meta |
| GET | `/entities/count` | astro_entities.json 总数 + type 分布 | entities |
| GET | `/entities/types` | 同 `/entities/count`,独立路径便于前端调用 | entities |
| GET | `/entities/sample?limit=N` | 取前 N 条样本(1-20,默认 3) | entities |
| GET | `/docs` | FastAPI 自动生成的 Swagger UI(开发态) | docs |
| GET | `/openapi.json` | OpenAPI schema(前端 codegen 用) | docs |

## 四、本地启动

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

启动后访问:

- `http://127.0.0.1:8000/` 项目元信息
- `http://127.0.0.1:8000/health` 健康检查
- `http://127.0.0.1:8000/docs` Swagger UI
- `http://127.0.0.1:8000/entities/count` 当前实体计数

**注意**:本机测完即关,不要让 uvicorn 后台常驻。

## 五、与数据层契约

后端只读 [`../data/astro_entities.json`](../data/astro_entities.json) 与 [`../data/planets_seed.json`](../data/planets_seed.json),**不**直连 SQLite(Phase 0 后续接入)。当前 Phase 0 实体总览:

- 实体来源:`scripts/md_to_astro_db.py` 抽取 02 / 04 / 06 md
- 当前总数(2026-08-31):`total=43`(branch 31 / story 2 / legend 2 / master 4 / quote 4)
- 种子:planets_seed.json 9 条(8 行星 + 冥王星矮行星),**未**合并到主 JSON(Phase 0 #2/#3/#4 正式抽取时统一合并)

## 六、阶段目标

| 阶段 | 截止 | 关键产物 | 当前状态 |
|------|------|----------|----------|
| Phase 1.1 后端骨架 | W2 Day 1(0831) | FastAPI + 5 个端点 | ✅ 本次提交 |
| Phase 1.2 业务路由 | W2 Day 4-5 | /sky /event /guide /catalog | ☐ |
| Phase 1.3 数据层接入 | W2 Day 6 | SQLite + HYG + 事件流 | ☐ |
| Phase 1.4 前端骨架 | W3 | React + 5 个页面骨架 | ☐ |
| Phase 1.5 Docker Compose | W4 | 一键启动 | ☐ |

## 七、相关文档

- [`../项目开发计划.md`](../项目开发计划.md) · 主开发计划(勾选项唯一权威)
- [`../README.md`](../README.md) · 项目入口
- [`../data/astro_entities.schema.md`](../data/astro_entities.schema.md) · 实体字段约定
- [`../scripts/md_to_astro_db.py`](../scripts/md_to_astro_db.py) · 抽取脚本

## 八、变更记录

| 日期 | 变更 | 备注 |
|------|------|------|
| 2026-08-31 | 首版后端骨架(5 端点 + requirements + 本 README) | W2 Day 1,接 Phase 1 起步 |

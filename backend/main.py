"""
AstronomyAdvisor · 后端入口
============================

Phase 1 · 步骤 1.1 起步:FastAPI 最小骨架(W2 Day 1, 2026-08-31 立)

端点(当前):
  GET  /                  项目元信息
  GET  /health            健康检查
  GET  /entities/count    读取 data/astro_entities.json 计数摘要
  GET  /entities/types    按 type 分组统计
  GET  /entities/sample   取前 N 条样本(默认 3,最多 20)

不做的:
  - 不启后台 server(本机测完即关,见 macOS 工作流约束)
  - 不接数据库(Phase 0 后续 SQLite 接入,这里只读 JSON)
  - 不接 LLM / 历算库(Phase 1 后段)
  - 不写鉴权(Phase 2 接飞书 OAuth)

启动:
  cd backend
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# 路径与常量
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_ENTITIES_PATH = PROJECT_ROOT / "data" / "astro_entities.json"

PROJECT_META = {
    "name": "AstronomyAdvisor",
    "name_cn": "天文顾问",
    "industry_code": "35-天文-Astronomy",
    "version": "0.1.0",
    "phase": "Phase 1 · W2 Day 1",
    "owner": "张勇",
}

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


class ProjectMeta(BaseModel):
    name: str
    name_cn: str
    industry_code: str
    version: str
    phase: str
    owner: str


class HealthResponse(BaseModel):
    status: str
    entities_loaded: bool
    entities_path: str


class EntityCount(BaseModel):
    total: int
    by_type: dict[str, int]


class EntitySample(BaseModel):
    total: int
    returned: int
    items: list[dict]


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def load_entities(path: Optional[Path] = None) -> list[dict]:
    """读取 data/astro_entities.json,缺失/解析失败抛 HTTPException。"""
    p = path or DEFAULT_ENTITIES_PATH
    if not p.exists():
        raise HTTPException(
            status_code=503,
            detail=f"astro_entities.json 缺失: {p}",
        )
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"astro_entities.json 解析失败: {e}",
        ) from e


# ---------------------------------------------------------------------------
# 应用
# ---------------------------------------------------------------------------

app = FastAPI(
    title=PROJECT_META["name"],
    description=PROJECT_META["name_cn"] + " · 后端 API",
    version=PROJECT_META["version"],
)


@app.get("/", response_model=ProjectMeta, tags=["meta"])
def root() -> ProjectMeta:
    """项目元信息(无依赖,不读 JSON)。"""
    return ProjectMeta(**PROJECT_META)


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """健康检查 + 数据文件可达性。"""
    p = DEFAULT_ENTITIES_PATH
    return HealthResponse(
        status="ok",
        entities_loaded=p.exists(),
        entities_path=str(p),
    )


@app.get("/entities/count", response_model=EntityCount, tags=["entities"])
def entities_count() -> EntityCount:
    """astro_entities.json 总数 + 按 type 分布。"""
    entities = load_entities()
    by_type = dict(Counter(e.get("type", "unknown") for e in entities))
    return EntityCount(total=len(entities), by_type=by_type)


@app.get("/entities/types", response_model=EntityCount, tags=["entities"])
def entities_types() -> EntityCount:
    """类型分布(同 /entities/count,保留独立路径便于前端调用)。"""
    return entities_count()


@app.get("/entities/sample", response_model=EntitySample, tags=["entities"])
def entities_sample(
    limit: int = Query(default=3, ge=1, le=20, description="返回条数(1-20)"),
) -> EntitySample:
    """取前 N 条样本(默认 3),用于前端联调。"""
    entities = load_entities()
    items = entities[:limit]
    return EntitySample(
        total=len(entities),
        returned=len(items),
        items=items,
    )


# ---------------------------------------------------------------------------
# 入口(本地手测:python main.py → uvicorn reload)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

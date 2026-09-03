# AstronomyAdvisor

> 35-天文-Astronomy 行业 Web 项目 · 内部代号 AstronomyAdvisor

## 项目说明
基于张勇的 36 行业架构,AstronomyAdvisor 是 天文-Astronomy 行业的 Web 端顾问产品。

## 同步
- GitHub: https://github.com/1500385678/AstronomyAdvisor
- Gitee: https://gitee.com/architectzy/AstronomyAdvisor

## 自动化
- T4 每日 02:00 检查项目并更新开发计划
- T5 每日 03:00 完成小步开发并 commit + push

## 当前状态 · 2026-09-04 凌晨

| 维度 | 数据 | commit |
| --- | --- | --- |
| Phase 0 #2 步 3(星座合并) | 9/88 闭项 | `d06a448` |
| Phase 0 #4 步 5(行星合并) | 9/9 闭项 | `276f4dc` |
| Phase 1 W2 后端骨架 | 5 端点 FastAPI | `70596d3` |
| 主 JSON total | 61(branch 31 / story 2 / legend 2 / master 4 / quote 4 / planet 9 / constellation 9) | — |

### 合并器 · 沙箱式运行
```bash
cd AstronomyWeb
python3 scripts/merge_constellations_seed.py   # 0903 步 3 合并器
python3 scripts/merge_planets_seed.py          # 0901 步 5 合并器
```
两脚本幂等(同 id 二次合并 = skipped,不重复追加)。

### 下一步(已 commit,留待 0904+ 批次)
- 88 星座 9/88 → 18 凑 27(NW/N4/N1 三批,每批 6 条需查 IAU 88 完整表)
- Phase 0 #3(200 亮星 HYG 数据库)/ #4(110 梅西耶)/ 事件库(0/20)三资产未启动
- Phase 1 frontend 未启(W2 余 3 日窗口)

### 关联
- `项目开发计划.md` 第 236-249 行 = Phase 0 资产盘点详注
- `天文顾问开发架构与计划.md` = 总架构 + 5 阶段路线
- `data/astro_entities.schema.md` = 6 type 字段权威定义(0829 + 0902 闭)

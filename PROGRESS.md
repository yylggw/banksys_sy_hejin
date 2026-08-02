# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> **作用**:记录当前状态、下一步、决策、踩坑。每次会话开始先读这里,结束时更新。
> **更新时机**:每个模块完成、每次决策、每次踩坑、每次会话结束时更新。
> **格式**:时间倒序,最新在最前。

---

## 当前状态

- **六步流程位置**:第④步 — 本地 CI 自检（运行全量自检后进入第⑤步 PR）
- **当前会话**:全部 4 个模块开发完成
- **阻塞项**:无

---

## 已完成的 TODO

### ✅ 第①步:建仓 + 配 Secrets

- [x] 创建本地 Git 仓库(`git init`)
- [x] 编写 `.gitignore`(排除 data/、models/、__pycache__、.env 等)
- [x] 编写 `README.md`(项目简介、技术栈、启动方式、端口说明)
- [x] 编写 `requirements.txt` + `requirements-dev.txt`
- [x] 编写 `Dockerfile` + `.dockerignore`
- [x] 编写 `run.py`(健康检查 8889 + Streamlit 8888)
- [x] 编写 `app/main.py`(Streamlit 入口) + `app/__init__.py`
- [x] 编写 `tests/test_app.py`(health 端点 3 用例)
- [x] 编写 `.github/workflows/ci.yml` + `cd.yml`
- [x] 编写 `deploy.sh`(端口回退 8888-8898)
- [x] 首次 commit + 创建 GitHub 仓库 `yylggw/banksys_sy_hejin` + push
- [x] ✋ 确认门 1:提示人类配置 GitHub Secrets ✅

### ✅ 第②步:开 feature 分支

- [x] 从 main 切 `feature/1-project-setup` 分支

### ✅ 第③步:本地模块化开发

**模块 1:基础工程结构** (commit ea07258)
- [x] app/main.py — Streamlit 多页面导航 + health 端点
- [x] 基础测试 — test_app.py(health 端点测试 3 用例)
- [x] 本地 CI 自检:ruff format/check + pytest ✅

**模块 2:数据分析页面** (commit f9786d)
- [x] app/pages/1_数据分析.py — 数据看板(概览、分布图、认购率分析、热力图)
- [x] app/utils/data_loader.py — 数据加载+缓存+统计
- [x] 测试 — test_data_loader.py(9 用例)
- [x] 本地 CI 自检 ✅

**模块 3:模型训练** (commit 1e207e2)
- [x] app/utils/model_utils.py — Pipeline(RandomForest + OneHotEncoder + StandardScaler)
- [x] 测试 — test_model_utils.py(4 用例)
- [x] 本地 CI 自检 ✅

**模块 4:在线预测页面** (commit 7511579)
- [x] app/pages/2_在线预测.py — 点选表单(14 字段)+预测展示+自动训练入口
- [x] 本地 CI 自检 ✅

### ✅ 第④步:本地 CI 自检 — 全绿 ✅

- [x] ruff format --check . ✅
- [x] ruff check . ✅
- [x] pytest --cov --cov-fail-under=80 ✅（16/16, 覆盖率 90%）
- [x] 模型门禁: AUC = 0.8918 ✅（≥ 0.75 达标）
- [x] ✋ 确认门 4:全绿，可以进入第⑤步 PR

### 第⑤步:触发 PR

- [ ] git push + gh pr create
- [ ] ✋ 确认门 5:报 PR 链接 + CI 状态

### 第⑥步:人工审核 → 合并 → CD

- [ ] (人)Review → (人)Merge → CD 自动触发
- [ ] AI 盯 CD 结果,汇报端口/健康检查
- [ ] ✋ 确认门 6:部署验证

---

## ADR(架构决策记录)

*(暂无)*

## GOTCHAS(踩坑记录)

- 测试数据量 (5 samples) 导致 stratified split 失败: `test_size=1 < n_classes=2` → 修复: 扩至 10 samples, 5 no + 5 yes
- Streamlit 页面中文文件名触发 ruff `N999` → 加 `# noqa: N999` 行首注释
- `.coverage` 最初被 track → 补 `.gitignore` 并 `git rm --cached`
- 本地 Python 3.14.6 与目标容器 Python 3.11 版本不同,但依赖兼容
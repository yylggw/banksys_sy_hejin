# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> **作用**:记录当前状态、下一步、决策、踩坑。每次会话开始先读这里,结束时更新。
> **更新时机**:每个模块完成、每次决策、每次踩坑、每次会话结束时更新。
> **格式**:时间倒序,最新在最前。

---

## 当前状态

- **六步流程位置**:尚未开始(第①步准备中)
- **当前会话目标**:填写 `00/01/PROGRESS` 并获人类确认后,正式进入第①步建仓
- **阻塞项**:先等人类确认这份计划

---

## 第一批 TODO

### 第①步:建仓 + 配 Secrets (待确认后执行)

- [ ] 创建本地 Git 仓库(`git init`)
- [ ] 编写 `.gitignore`(排除 data/、models/、__pycache__、.env 等)
- [ ] 编写 `README.md`(项目简介、技术栈、启动方式、端口说明)
- [ ] 编写 `requirements.txt`(生产依赖:streamlit、scikit-learn、pandas、matplotlib、seaborn、joblib)
- [ ] 编写 `requirements-dev.txt`(开发依赖 + lint:ruff、pytest、pytest-cov)
- [ ] 编写 `Dockerfile`(基于 python:3.11-slim,安装依赖,暴露 8888,设置 healthcheck)
- [ ] 编写 `.dockerignore`
- [ ] 编写 `app/__init__.py` + `app/main.py`(Streamlit 入口,含 `/health` 端点)
- [ ] 编写 `app/utils/__init__.py` + `app/utils/data_loader.py` + `app/utils/model_utils.py`
- [ ] 编写 `tests/` 基础测试
- [ ] 编写 `.github/workflows/ci.yml`
- [ ] 编写 `.github/workflows/cd.yml`(占位,待服务器信息确认后填充)
- [ ] 首次 `git commit` + 创建 GitHub 仓库 + push
- [ ] ✋ **确认门 1**:提示人类配置 GitHub Secrets(SSH_PRIVATE_KEY/SSH_HOST/SSH_USER)

### 第②步:开 feature 分支

- [ ] 从 main 切 `feature/1-hello-app` 分支

### 第③步:本地模块化开发 (按模块分期)

**模块 1:基础工程结构**
- [ ] app/main.py — Streamlit 多页面导航 + health 端点
- [ ] 基础测试 — test_app.py(health 端点测试)
- [ ] 本地 CI 自检:ruff format/check + pytest
- [ ] ✋ 汇报进度

**模块 2:数据分析页面**
- [ ] app/pages/1_数据分析.py — 数据看板(概览、分布图、认购率分析、热力图)
- [ ] 测试 — test_data_loader.py
- [ ] 本地 CI 自检
- [ ] ✋ 汇报进度

**模块 3:模型训练**
- [ ] app/utils/model_utils.py — 训练 pipeline(RandomForest + 编码 + 标准化)
- [ ] 测试 — test_model_utils.py(训练重现性、预测格式、缺失模型处理)
- [ ] 本地 CI 自检
- [ ] ✋ 汇报进度

**模块 4:在线预测页面**
- [ ] app/pages/2_在线预测.py — 点选表单 + 预测展示
- [ ] 扩展测试(预测流程)
- [ ] 本地 CI 自检
- [ ] ✋ 汇报进度

### 第④步:本地 CI 自检

- [ ] ruff format --check . + ruff check .
- [ ] pytest --cov --cov-fail-under=80
- [ ] ✋ 确认门 4:全绿才继续

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

*(暂无)*
# PROGRESS · 项目进度 〔本项目活记忆 · AI 维护〕

> **作用**:记录当前状态、下一步、决策、踩坑。每次会话开始先读这里,结束时更新。
> **更新时机**:每个模块完成、每次决策、每次踩坑、每次会话结束时更新。
> **格式**:时间倒序,最新在最前。

---

## 当前状态

- **六步流程位置**:✅ **全部完成 — CI + CD 全绿**
- **最终部署**: 服务端口 `8899`（自动回退），健康检查通过
- **下一步**: 如有新功能需求可开新分支继续开发

---

## 全部已完成

### ✅ 第①步:建仓 + 配 Secrets

- [x] 创建本地 Git 仓库
- [x] 编写 `.gitignore`、`README.md`、`requirements.txt`、`requirements-dev.txt`
- [x] 编写 `Dockerfile`、`.dockerignore`、`run.py`、`deploy.sh`
- [x] 编写 `app/main.py`(Streamlit 入口) + `app/__init__.py`
- [x] 编写 `tests/test_app.py`(health 端点 3 用例)
- [x] 编写 `.github/workflows/ci.yml` + `cd.yml`
- [x] 首次 commit + 创建 GitHub 仓库 `yylggw/banksys_sy_hejin` + push
- [x] ✋ 确认门 1:提示人类配置 GitHub Secrets ✅

### ✅ 第②步:开 feature 分支

- [x] 从 main 切 `feature/1-project-setup` 分支

### ✅ 第③步:本地模块化开发

- [x] **模块 1**: app/main.py + run.py(health) + requirements + Dockerfile + CI/CD 基础
- [x] **模块 2**: app/pages/1_数据分析.py + app/utils/data_loader.py + 9 个测试
- [x] **模块 3**: app/utils/model_utils.py(RandomForest Pipeline) + 4 个测试, AUC=0.8918
- [x] **模块 4**: app/pages/2_在线预测.py(14 字段点选表单 + 预测结果展示 + 自动训练入口)

### ✅ 第④步:本地 CI 自检

- [x] `ruff format --check .` ✅
- [x] `ruff check .` ✅
- [x] `pytest 16/16` ✅ (覆盖率 app/utils 90%, ≥ 80%)
- [x] 模型门禁: AUC = 0.8918 ✅ (≥ 0.75)

### ✅ 第⑤步:触发 PR

- [x] `git push` → `gh pr create` → CI 全绿 ✅
- [x] ✋ 确认门 5: PR #1 链接 + CI 状态

### ✅ 第⑥步:人工审核 → 合并 → CD

- [x] PR #1 由人工 (yylggw) Review 并 Merge ✅
- [x] CD 自动触发: SCP 上传源码 → SSH → Docker build(Tsinghua 镜像源) → run → healthcheck
- [x] **最终部署端口: 8899**（8888 被占用，自动回退）
- [x] **健康检查通过** ✅
- [x] ✋ 确认门 6: 部署成功

---

## ADR(架构决策记录)

| 决策 | 内容 |
|---|---|
| 健康检查方式 | 用独立 HTTP server(8889) 而非 Streamlit 内置，避免 Streamlit 无运行时问题 |
| 部署策略 | 源码 SCP → 服务器 Docker build，而非传输完整镜像包（避免大文件上传） |
| pip 镜像源 | CD 构建时使用 `pypi.tuna.tsinghua.edu.cn` 加速依赖安装 |
| 端口策略 | 容器内 8888 固定，主机端口 8888-8908 自动回退，`docker rm -f` 幂等替换 |

## GOTCHAS(踩坑记录)

| 坑 | 现象 | 修复 |
|---|---|---|
| 测试数据过少 | `stratify` 分层抽样失败 | 扩到 10 samples，5 yes + 5 no |
| 中文文件名 | ruff N999 报错 | 行首加 `# noqa: N999` |
| `.coverage` 进 Git | 本地缓存被 track | 补 `.gitignore` 并 `git rm --cached` |
| SCP 文件列表 | `source` 多行 YAML 语法无效，tar 空存档 | 改用逗号分隔字符串 |
| 服务器 apt 源慢 | apt-get update 跑 7+ 分钟 | 直接使用默认源（仅安装 curl 小包） |
| 服务器 pip 源慢 | pip install 跑 15+ 分钟 | CD 用 `--build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple` |
| SSH 超时 | 部署步骤 20m 不够 | `command_timeout: 30m` |
| 旧容器占端口 | 端口区间 8888-8898 全占满 | 先 `docker rm -f` + 扩区间到 8908
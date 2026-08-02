# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_hejin` — 银行营销预测系统
- **一句话目标**:基于银行营销数据集,提供一个交互式数据分析看板 + 在线认购预测系统,让业务人员能够直观理解客户特征并通过点选输入快速获取预测结果。
- **使用者/受益者**:银行营销人员/数据分析师 — 通过数据洞察和预测工具提高营销转化率。
- **核心功能**:
  - **数据分析交互页面**:对银行营销数据进行多维度可视化探索(客户画像、特征分布、认购率分析等)
  - **离线训练 + 在线预测系统**:训练分类模型,提供点选表单预测客户是否会认购定期存款
- **输入/数据**:UCI Bank Marketing 风格数据集(`data/train.csv`、`data/test.csv`,约 4 万条,22 列,目标字段 `subscribe`)。**数据不进入 Git**(已在 `.gitignore` 排除)。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 数据科学生态成熟,适合 ML + Web 快速原型 |
| Web/API 框架 | **Streamlit** | 一套代码同时实现数据分析看板 + 预测表单,无需前后端分离 |
| 测试 | pytest + pytest-cov | Python 生态标准测试框架,支持覆盖率 |
| 格式/静态检查 | ruff (format + check) | 速度快,规则全面,替代 flake8/isort/black 三件套 |
| ML 框架 | scikit-learn | 经典库,适合表格数据二分类任务,与 Streamlit 配合良好 |
| 打包/运行 | Docker | 环境一致化,支持 CI/CD 自动构建与部署 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_hejin/
├── standards/                 # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   └── 06-ai-collab-protocol.md
├── app/                       # Streamlit 应用主目录
│   ├── __init__.py
│   ├── main.py                # 应用入口(导航)
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 1_数据分析.py      # 数据分析看板
│   │   └── 2_在线预测.py      # 在线预测表单
│   └── utils/
│       ├── __init__.py
│       ├── data_loader.py     # 数据加载与预处理
│       └── model_utils.py     # 模型训练、保存、预测
├── models/                    # 训练产物(已 gitignore)
│   └── .gitkeep               # 仅占位,实际模型不进 Git
├── tests/                     # 测试目录
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_model_utils.py
│   └── test_app.py
├── data/                      # 原始数据(已 gitignore)
│   ├── train.csv
│   └── test.csv
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile                 # 容器构建
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── ci.yml                 # CI: PR 触发,运行 lint + test + build
│   └── cd.yml                 # CD: main 合并触发,自动部署
└── README.md                  # 项目说明
```

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` (发现并执行 tests/ 下所有测试) |
| 覆盖率 | `>= 80%` (核心逻辑 `app/utils/`) |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | 模型 AUC >= 0.75 (二分类任务);数据加载成功率 100% |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物 **不进 Git**(已在 `.gitignore` 配置)。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_hejin` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_hejin` | 服务器部署目录 |
| `<PORT>` | `8888` | 服务端口(容器内固定;主机端口自动回退) |
| `<PORT_MAX>` | `8898` | 端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `health` | 健康检查地址 |
| `<SSH_USER>` | (待定) | 由 GitHub Secrets 配置 |
| `<SSH_HOST>` | (待定) | 由 GitHub Secrets 配置 |
# banksys_sy_hejin · 银行营销预测系统

基于银行营销数据集，提供**数据分析看板** + **在线认购预测**的 Web 应用。

## 技术栈

| 层 | 选型 |
|---|---|
| 语言 | Python 3.11 |
| Web 框架 | Streamlit |
| 测试 | pytest + pytest-cov |
| 格式/静态检查 | ruff (format + check) |
| ML 框架 | scikit-learn |
| 容器化 | Docker |
| CI/CD | GitHub Actions |

## 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app/main.py --server.port 8888

# 访问
open http://localhost:8888
```

## Docker

```bash
docker build -t banksys_sy_hejin .
docker run -d --name banksys_sy_hejin -p 8888:8888 banksys_sy_hejin
```

## 目录结构

```
banksys_sy_hejin/
├── app/           # Streamlit 应用
├── standards/     # 项目记忆与规范
├── tests/         # 测试
├── data/          # 原始数据 (不进 Git)
├── models/        # 模型产物 (不进 Git)
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── .github/workflows/
```

## 项目状态

详情见 [PROGRESS.md](PROGRESS.md) 和 [standards/](standards/README.md)。
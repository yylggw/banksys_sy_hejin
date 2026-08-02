# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |

---

## 2. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、风险、边界>
```

---

## 3. 需求清单

### US-1 项目工程化与 CI/CD 基础设施 · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备完整的工程结构(目录、依赖、Docker、CI、CD),
以便 后续每次开发都能自动检查代码质量并自动部署上线。

验收标准:
- AC1: 项目目录结构符合 `00-project-context.md` 的目录地图,关键文件(`app/main.py`,`requirements.txt`,`Dockerfile`)已就位。
- AC2: `ruff format --check .` 和 `ruff check .` 零错误通过。
- AC3: `pytest --cov --cov-fail-under=80` 通过(覆盖率 ≥ 80%)。
- AC4: `docker build` 成功,镜像运行后 `curl http://localhost:8888/health` 返回 `{"status":"ok"}`。
- AC5: GitHub Actions CI 在 PR 触发时自动运行 lint → test → build。
- AC6: GitHub Actions CD 在合并 main 时自动部署到服务器,健康检查通过。
- AC7: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 本地不强制 Docker;`docker build` 交给 CI 执行。
- 数据文件进 `.gitignore`,模型产物进 `.gitignore`。

---

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行营销人员**,
我想要 一个交互式数据看板,
以便 直观了解客户整体画像、各特征分布、以及认购率的关联关系。

验收标准:
- AC1: Given 数据已加载,When 用户访问数据分析页面,Then 显示数据集概览(总记录数、字段列表、基本统计量)。
- AC2: Given 页面加载完毕,When 用户查看客户画像,Then 显示年龄分布直方图、职业/婚姻/教育分布条形图。
- AC3: Given 页面加载完毕,When 用户查看认购分析,Then 显示 subscribe 目标分布饼图,以及各特征分组下的认购率对比柱状图(如按职业、教育水平)。 
- AC4: Given 页面加载完毕,When 用户查看数值特征,Then 显示数值特征的描述性统计表和相关性热力图。
- AC5: 所有图表使用 Streamlit 原生组件渲染,无外部 JS 依赖。
- AC6: 页面加载时间(数据读取后)< 5 秒。

技术备注:
- 数据从 `data/train.csv` 加载,使用 Streamlit `@st.cache_data` 缓存。
- 可视化使用 `matplotlib` + `seaborn` 生成静态图,嵌入 Streamlit。

---

### US-3 离线训练 + 在线预测系统 · 状态: Backlog

作为 **银行营销人员**,
我想要 基于历史数据训练一个预测模型,并通过点选表单输入客户信息,实时获取"是否会认购定期存款"的预测结果,
以便 在营销活动中快速筛选高潜力客户。

验收标准:
- AC1: 训练脚本可复现执行:`python app/utils/model_utils.py` 或通过 Streamlit 页面触发训练,输出模型文件到 `models/` 目录。
- AC2: 训练完成后,模型在测试集上的 AUC >= 0.75。
- AC3: 预测页面提供点选式表单,包含以下字段:
  - 年龄(滑块:18-100)
  - 职业(下拉选择:admin., blue-collar, entrepreneur, housemaid, management, retired, self-employed, services, student, technician, unemployed)
  - 婚姻状况(单选:married, single, divorced)
  - 教育水平(下拉选择:basic.4y, basic.6y, basic.9y, high.school, professional.course, university.degree, unknown)
  - 是否有房贷(单选:yes, no, unknown)
  - 是否有个人贷款(单选:yes, no, unknown)
  - 联系方式(单选:cellular, telephone)
  - 上次营销结果(单选:failure, nonexistent, success)
  - 活动天数(滑块:1-1000)
  - 历史活动次数(滑块:0-50)
  - 就业率变化率(滑块:-5 到 5)
  - 消费价格指数(滑块:90-100)
  - 消费者信心指数(滑块:-60 到 0)
  - 3 月期贷款利率(滑块:0-20)
  - 就业人数(滑块:4900-5300)
- AC4: 点击预测按钮后,页面显示预测结果(认购/不认购)及概率百分比。  
- AC5: 预测响应时间 < 1 秒(模型已加载后)。
- AC6: 如果模型不存在,页面提示"模型未训练,请先训练"并提供一键训练入口。

技术备注:
- 使用 scikit-learn 的 `RandomForestClassifier` 作为基线模型。
- 模型序列化使用 `joblib`。
- 特征工程:pipelines 包含编码(OneHotEncoder/OrdinalEncoder)与标准化(StandardScaler)。

---

### US-4 预测页面多场景输入 · 状态: Backlog

作为 **银行营销人员**,
我想要 在预测页面中能灵活切换"默认值"、"典型客户模板"等场景,
以便 快速测试不同客户画像下的预测结果。

验收标准:
- AC1: 页面提供"清空为默认值"按钮,一键重置所有表单字段为默认值。
- AC2: (可选)页面提供 2-3 个典型客户预设(如"高净值客户"、"年轻蓝领"),点击即可填充对应字段值。

技术备注:
- 此需求优先级低于 US-3,可延后实现。

---

## 4. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑(`app/utils/`)必须有单元测试,覆盖率 ≥ 80%。
- **可部署**:部署后健康检查(`/health`)必须返回 `{"status":"ok"}`。
- **性能**:预测接口响应 < 1 秒;数据分析页面加载(不含首次数据读取)< 3 秒。
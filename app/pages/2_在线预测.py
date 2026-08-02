# noqa: N999 — Streamlit 需要中文文件名做页面标题
"""
在线预测页面。

提供点选式表单输入客户信息，调用训练好的模型预测是否会认购定期存款。
"""

import pandas as pd
import streamlit as st

from app.utils.data_loader import CATEGORICAL_COLS, NUMERICAL_COLS
from app.utils.model_utils import load_model, predict, train

# ---- 选项常量 ----

JOB_OPTIONS = [
    "admin.",
    "blue-collar",
    "entrepreneur",
    "housemaid",
    "management",
    "retired",
    "self-employed",
    "services",
    "student",
    "technician",
    "unemployed",
]

MARITAL_OPTIONS = ["married", "single", "divorced"]
EDUCATION_OPTIONS = [
    "basic.4y",
    "basic.6y",
    "basic.9y",
    "high.school",
    "professional.course",
    "university.degree",
    "unknown",
]
YES_NO_OPTIONS = ["yes", "no"]
YES_NO_UNKNOWN_OPTIONS = ["yes", "no", "unknown"]
CONTACT_OPTIONS = ["cellular", "telephone"]
POUTCOME_OPTIONS = ["failure", "nonexistent", "success"]


def _render_form() -> dict:
    """渲染点选输入表单，返回特征值字典。"""
    st.subheader("📝 客户信息输入")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**人口统计信息**")
        age = st.slider("年龄", min_value=18, max_value=100, value=35, help="客户年龄")
        job = st.selectbox("职业", JOB_OPTIONS, index=0)
        marital = st.radio("婚姻状况", MARITAL_OPTIONS, horizontal=True)
        education = st.selectbox("教育水平", EDUCATION_OPTIONS, index=5)

        st.markdown("**金融与联系信息**")
        default = st.selectbox("是否有违约记录", YES_NO_UNKNOWN_OPTIONS, index=1)
        housing = st.radio("是否有房贷", YES_NO_OPTIONS, horizontal=True)
        loan = st.radio("是否有个人贷款", YES_NO_OPTIONS, horizontal=True)
        contact = st.radio("联系方式", CONTACT_OPTIONS, horizontal=True)

    with col2:
        st.markdown("**营销活动信息**")
        poutcome = st.selectbox(
            "上次营销结果",
            POUTCOME_OPTIONS,
            index=1,
            help="success=成功, failure=失败, nonexistent=之前未联系",
        )
        campaign = st.number_input(
            "本次营销联系次数",
            min_value=0,
            max_value=50,
            value=1,
            help="本次活动中联系该客户的次数",
        )
        previous = st.number_input(
            "历史联系次数",
            min_value=0,
            max_value=50,
            value=0,
            help="本次之前联系该客户的次数",
        )
        pdays = st.number_input(
            "上次联系距今天数",
            min_value=0,
            max_value=1000,
            value=999,
            help="999 表示从未联系过",
        )
        duration = st.number_input(
            "上次通话时长(秒)",
            min_value=0,
            max_value=5000,
            value=200,
            help="上次通话时长",
        )

        st.markdown("**经济背景指标**")
        emp_var_rate = st.slider(
            "就业率变化率", min_value=-5.0, max_value=5.0, value=0.0, step=0.1
        )
        cons_price_index = st.slider(
            "消费价格指数", min_value=90.0, max_value=100.0, value=93.0, step=0.1
        )
        cons_conf_index = st.slider(
            "消费者信心指数", min_value=-60.0, max_value=0.0, value=-40.0, step=0.1
        )
        lending_rate3m = st.slider(
            "3月期贷款利率", min_value=0.0, max_value=20.0, value=3.0, step=0.1
        )
        nr_employed = st.slider(
            "就业人数(千人)", min_value=4900.0, max_value=5300.0, value=5050.0, step=0.1
        )

    return {
        "age": age,
        "job": job,
        "marital": marital,
        "education": education,
        "default": default,
        "housing": housing,
        "loan": loan,
        "contact": contact,
        "month": "may",
        "day_of_week": "mon",
        "duration": duration,
        "campaign": campaign,
        "pdays": pdays,
        "previous": previous,
        "poutcome": poutcome,
        "emp_var_rate": emp_var_rate,
        "cons_price_index": cons_price_index,
        "cons_conf_index": cons_conf_index,
        "lending_rate3m": lending_rate3m,
        "nr_employed": nr_employed,
    }


def _render_result(pred_result: dict) -> None:
    """渲染预测结果。"""
    if "error" in pred_result:
        st.error(f"❌ {pred_result['error']}")
        return

    prediction = pred_result["prediction"]
    prob_sub = pred_result["probability_subscribe"] * 100

    _col1, col2, _col3 = st.columns([1, 2, 1])
    with col2:
        if prediction == "yes":
            st.success("## ✅ 预测结果：**会认购**")
        else:
            st.warning("## ❌ 预测结果：**不会认购**")

        st.metric("认购概率", f"{prob_sub:.1f}%")

        # 概率可视化
        st.markdown("**认购概率**")
        st.progress(int(prob_sub), text=f"{prob_sub:.1f}%")


def _reset_form() -> None:
    """重置所有表单字段为默认值。"""
    keys = list(st.session_state.keys())
    for k in keys:
        del st.session_state[k]


def main() -> None:
    """在线预测页主入口。"""
    st.title("🤖 在线预测")
    st.markdown("通过点选表单输入客户信息，预测该客户是否会认购定期存款。")

    # 加载模型
    model = load_model()

    # 模型不存在 → 提供训练入口
    if model is None:
        st.warning("⚠️ 模型尚未训练，请先训练模型后再进行预测。")
        if st.button("🚀 开始训练模型（约 30 秒）", type="primary"):
            with st.spinner("正在训练模型..."):
                try:
                    metrics = train()
                    st.success(f"✅ 模型训练完成！验证集 AUC: **{metrics['auc']}**")
                    st.rerun()
                except FileNotFoundError:
                    st.error(
                        "❌ 未找到训练数据。请确认 `data/train.csv` 存在于项目目录中。"
                    )
                except Exception as e:  # noqa: BLE001
                    st.error(f"❌ 训练失败: {e}")
        return

    # 表单区域
    with st.form("prediction_form"):
        features = _render_form()

        _col1, col2, _col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button(
                "🔮 预测", type="primary", use_container_width=True
            )

    if submitted:
        with st.spinner("正在预测..."):
            df = pd.DataFrame([features])
            # 确保列顺序与训练时一致
            df = df[CATEGORICAL_COLS + NUMERICAL_COLS]
            result = predict(df, model)
            _render_result(result)

    st.markdown("---")
    st.caption("模型: RandomForestClassifier (scikit-learn) | 数据: data/train.csv")


if __name__ == "__main__":
    main()

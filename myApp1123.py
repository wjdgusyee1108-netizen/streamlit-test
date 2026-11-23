import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="매출 대시보드", layout="wide")
st.title("📊 월별 매출 대시보드")

# 샘플 데이터 생성
@st.cache_data
def load_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    categories = ["전자기기", "의류", "식품"]
    rows = []
    for d in dates:
        for c in categories:
            sales = int(rng.integers(100, 1000)) * 1000
            orders = int(rng.integers(5, 50))
            rows.append({"날짜": d, "카테고리": c, "매출": sales, "주문수": orders})
    return pd.DataFrame(rows)

df = load_data()

# 사이드바 필터
st.sidebar.header("필터 설정")
selected_cats = st.sidebar.multiselect(
    "카테고리 선택",
    options=df["카테고리"].unique(),
    default=df["카테고리"].unique(),
)
min_date, max_date = df["날짜"].min().date(), df["날짜"].max().date()
date_range = st.sidebar.date_input("기간 선택", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# 데이터 필터링
filtered = df[df["카테고리"].isin(selected_cats)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[(filtered["날짜"] >= start_d) & (filtered["날짜"] <= end_d)]

# KPI 지표
col1, col2, col3 = st.columns(3)
total_sales = filtered["매출"].sum()
total_orders = filtered["주문수"].sum()
avg_order = int(total_sales / total_orders) if total_orders > 0 else 0

col1.metric("총 매출", f"{total_sales:,.0f}원")
col2.metric("총 주문수", f"{total_orders:,}건")
col3.metric("평균 주문금액", f"{avg_order:,.0f}원")

# 차트 시각화
st.subheader("카테고리별 일간 매출 추이")
if not filtered.empty:
    pivot_df = filtered.pivot_table(index="날짜", columns="카테고리", values="매출", aggfunc="sum", fill_value=0)
    st.line_chart(pivot_df)
else:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

# 원본 데이터 테이블
st.subheader("상세 데이터")
st.dataframe(filtered.sort_values("날짜", ascending=False), use_container_width=True)

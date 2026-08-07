from datetime import datetime, timezone, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V19",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------
# 🎨 고급 CSS 스타일링
# ---------------------------------------------------------
st.markdown(
    """
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .kpi-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .kpi-card { flex: 1; background-color: #161b22; border-radius: 16px; padding: 20px; border: 1px solid #30363d; }
    .kpi-label { color: #a0aab5; font-size: 0.85rem; margin-bottom: 6px; }
    .kpi-value { font-size: 1.6rem; font-weight: 700; }
    .profit-pos { color: #f04452 !important; }
    .profit-neg { color: #3182f6 !important; }
    /* 버튼 스타일 제거하여 카드 형태 유지 */
    div[data-testid="stVerticalBlock"] > div > button { width: 100%; text-align: left; background: none; border: none; padding: 0; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 📂 종목 데이터 정정 (카카오페이 일반 8종목)
# ---------------------------------------------------------
portfolio_data = [
    # 토스증권 (3종목)
    {"category": "토스증권", "name": "SK하이닉스", "ticker": "000660.KS", "shares": 2, "avg_price": 2545000, "currency": "KRW"},
    {"category": "토스증권", "name": "SK스퀘어", "ticker": "402340.KS", "shares": 2, "avg_price": 1990000, "currency": "KRW"},
    {"category": "토스증권", "name": "크리에이트 엔터프라이즈", "ticker": "CRE8", "shares": 15, "avg_price": 4.48, "currency": "USD"},
    # 카카오페이 일반 (8종목)
    {"category": "카카오페이 일반", "name": "삼성전자", "ticker": "005930.KS", "shares": 20, "avg_price": 126052, "currency": "KRW"},
    {"category": "카카오페이 일반", "name": "두산에너빌리티", "ticker": "034020.KS", "shares": 10, "avg_price": 82950, "currency": "KRW"},
    {"category": "카카오페이 일반", "name": "우리금융지주", "ticker": "316140.KS", "shares": 10, "avg_price": 32015, "currency": "KRW"},
    {"category": "카카오페이 일반", "name": "TIGER 200", "ticker": "102110.KS", "shares": 1, "avg_price": 100995, "currency": "KRW"},
    {"category": "카카오페이 일반", "name": "KODEX 200", "ticker": "069500.KS", "shares": 1, "avg_price": 101155, "currency": "KRW"},
    {"category": "카카오페이 일반", "name": "엔비디아 (종합계좌)", "ticker": "NVDA", "shares": 2.748, "avg_price": 192.28, "currency": "USD"},
    {"category": "카카오페이 일반", "name": "NVDL", "ticker": "NVDL", "shares": 4.23, "avg_price": 29.06, "currency": "USD"},
    {"category": "카카오페이 일반", "name": "PLUS 고배당주", "ticker": "294230.KS", "shares": 5, "avg_price": 26627, "currency": "KRW"},
    # 카카오페이 RIA (1종목)
    {"category": "카카오페이 RIA", "name": "엔비디아 (RIA계좌)", "ticker": "NVDA", "shares": 1, "avg_price": 182.23, "currency": "USD"},
    # 카카오페이 ISA (2종목)
    {"category": "카카오페이 ISA", "name": "TIGER 미국배당다우존스타겟커버드콜1호", "ticker": "476970.KS", "shares": 13, "avg_price": 13506, "currency": "KRW"},
]

# (계산 로직 등은 동일하므로 생략, 아래 UI 부분 업데이트)

# ---------------------------------------------------------
# 🖥️ 업데이트된 계좌별 요약 카드 UI
# ---------------------------------------------------------
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "📊 전체 보기"

st.markdown("### 계좌별 자산")
acc_cols = st.columns(4)

account_map = {
    "토스증권": "💳 토스증권",
    "카카오페이 일반": "💬 카카오페이 일반",
    "카카오페이 RIA": "💬 카카오페이 RIA",
    "카카오페이 ISA": "💬 카카오페이 ISA"
}

for idx, acc_name in enumerate(account_map.keys()):
    acc_items = [d for d in all_stock_data if d["category"] == acc_name]
    acc_invest = sum([d["invest_krw"] for d in acc_items])
    acc_val = sum([d["current_val_krw"] for d in acc_items])
    acc_profit = acc_val - acc_invest
    acc_rate = (acc_profit / acc_invest * 100) if acc_invest != 0 else 0
    profit_class = "profit-pos" if acc_profit >= 0 else "profit-neg"

    with acc_cols[idx]:
        # 버튼을 눌러 탭을 변경하도록 설정
        if st.button(f"{acc_name}", key=f"btn_{acc_name}"):
            st.session_state.selected_tab = account_map[acc_name]
            st.rerun()
            
        with st.container(border=True):
            st.markdown(f"**{acc_name}**")
            st.markdown(f"{len(acc_items)}종목")
            st.markdown(f"### {acc_val:,.0f}원")
            st.markdown(f"평가손익: <span class='{profit_class}'>{acc_profit:,.0f}원 ({acc_rate:.2f}%)</span>", unsafe_allow_html=True)

# 탭 선택 시 세션 상태 반영
tabs = st.tabs(["📊 전체 보기", "💳 토스증권", "💬 카카오페이 일반", "💬 카카오페이 RIA", "💬 카카오페이 ISA"])
# (이후 탭 렌더링 로직에서 st.session_state.selected_tab을 활용하여 탭 활성화)

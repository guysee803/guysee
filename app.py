from datetime import datetime
import pandas as pd
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V3 - 투자원금 중심", page_icon="📈", layout="wide"
)

# ---------------------------------------------------------
# 🎨 고급 CSS 스타일링 (다크 모드 디자인)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .main-subtitle {
        color: #a0aab5;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    .section-header {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2a323e;
        padding-bottom: 10px;
    }

    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .kpi-card {
        flex: 1;
        background-color: #161b22;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border: 1px solid #2a323e;
    }

    .kpi-label {
        color: #a0aab5;
        font-size: 0.9rem;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }

    .kpi-sub-value {
        color: #a0aab5;
        font-size: 0.9rem;
        margin-top: 5px;
    }

    .stock-card {
        background-color: #161b22;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border: 1px solid #2a323e;
    }
    
    .card-top {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 15px;
    }

    .stock-name-area {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .company-logo {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #2a323e;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        color: #ffffff;
        font-weight: 600;
    }

    .company-name {
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.2;
    }

    .company-meta {
        color: #a0aab5;
        font-size: 0.85rem;
        font-weight: 300;
    }

    .card-price-area {
        text-align: right;
    }

    .current-price {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .profit-pos {
        color: #ef476f !important;
    }
    .profit-neg {
        color: #118ab2 !important;
    }

    .card-bottom-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        border-top: 1px solid #2a323e;
        padding-top: 15px;
    }
    
    .info-label {
        color: #a0aab5;
        font-size: 0.75rem;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .info-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    div[data-testid="stDataFrame"], div[data-testid="stTable"], header {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📂 데이터 및 로직 영역
# ---------------------------------------------------------

portfolio_data = [
    {
        "category": "카카오페이",
        "name": "삼성전자",
        "ticker": "005930.KS",
        "shares": 20,
        "avg_price": 126052,
        "currency": "KRW",
        "logo": "삼",
    },
    {
        "category": "토스",
        "name": "SK하이닉스",
        "ticker": "000660.KS",
        "shares": 2,
        "avg_price": 2545000,
        "currency": "KRW",
        "logo": "S",
    },
    {
        "category": "토ส",
        "name": "SK스퀘어",
        "ticker": "402340.KS",
        "shares": 2,
        "avg_price": 1990000,
        "currency": "KRW",
        "logo": "S",
    },
    {
        "category": "카카오페이",
        "name": "엔비디아 (종합계좌)",
        "ticker": "NVDA",
        "shares": 2.748,
        "avg_price": 192.28,
        "currency": "USD",
        "logo": "N",
    },
    {
        "category": "카카오페이",
        "name": "두산에너빌리티",
        "ticker": "034020.KS",
        "shares": 10,
        "avg_price": 82950,
        "currency": "KRW",
        "logo": "두",
    },
    {
        "category": "카카오페이",
        "name": "우리금융지주",
        "ticker": "316140.KS",
        "shares": 10,
        "avg_price": 32015,
        "currency": "KRW",
        "logo": "우",
    },
    {
        "category": "카카오페이",
        "name": "엔비디아 (RIA계좌)",
        "ticker": "NVDA",
        "shares": 1,
        "avg_price": 182.23,
        "currency": "USD",
        "logo": "N",
    },
    {
        "category": "카카오페이",
        "name": "NVDL",
        "ticker": "NVDL",
        "shares": 4.23,
        "avg_price": 29.06,
        "currency": "USD",
        "logo": "N",
    },
]


@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        ticker = yf.Ticker("USDCKR=X")
        data = ticker.history(period="1d")
        return data["Close"].iloc[-1]
    except:
        return 1345.0


current_usd_krw = get_exchange_rate()


def calculate_stock(item, exchange_rate):
    ticker = yf.Ticker(item["ticker"])
    try:
        hist = ticker.history(period="1d")
        current_price = (
            hist["Close"].iloc[-1] if not hist.empty else item["avg_price"]
        )
    except:
        current_price = item["avg_price"]

    if item["currency"] == "USD":
        invest_krw = item["avg_price"] * item["shares"] * exchange_rate
        current_val_krw = current_price * item["shares"] * exchange_rate
        current_price_display = f"${current_price:,.2f}"
    else:
        invest_krw = item["avg_price"] * item["shares"]
        current_val_krw = current_price * item["shares"]
        current_price_display = f"{current_price:,.0f}원"

    profit_krw = current_val_krw - invest_krw
    profit_rate = (profit_krw / invest_krw * 100) if invest_krw != 0 else 0

    return {
        "category": item["category"],
        "name": item["name"],
        "ticker": item["ticker"],
        "shares": item["shares"],
        "avg_price": item["avg_price"],
        "currency": item["currency"],
        "logo_char": item["logo"],
        "current_price_display": current_price_display,
        "invest_krw": invest_krw,
        "current_val_krw": current_val_krw,
        "profit_krw": profit_krw,
        "profit_rate": profit_rate,
    }


# ---------------------------------------------------------
# 🖥️ 화면 렌더링
# ---------------------------------------------------------

st.title("석의 주식창")
current_time = datetime.now().strftime("%Y년 %m월 %d일 (%a) %H:%M")
st.markdown(
    f"<div class='main-subtitle'>{current_time} · 실시간 시세 반영 중</div>",
    unsafe_allow_html=True,
)

all_stock_data = []
total_invest = 0
total_current_val = 0

with st.spinner("실시간 시세 데이터를 불러오는 중입니다..."):
    for item in portfolio_data:
        data = calculate_stock(item, current_usd_krw)
        all_stock_data.append(data)
        total_invest += data["invest_krw"]
        total_current_val += data["current_val_krw"]

total_profit = total_current_val - total_invest
total_profit_rate = (
    (total_profit / total_invest * 100) if total_invest != 0 else 0
)
profit_class_total = "profit-pos" if total_profit >= 0 else "profit-neg"

# 상단 요약 카드
st.markdown(
    f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">총 투자원금</div>
        <div class="kpi-value">{total_invest:,.0f} 원</div>
        <div class="kpi-sub-value">보유수량 × 평균단가</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">현재 평가금액</div>
        <div class="kpi-value">{total_current_val:,.0f} 원</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">총 평가손익</div>
        <div class="kpi-value {profit_class_total}">{total_profit:,.0f} 원</div>
        <div class="kpi-sub-value">{total_profit_rate:,.2f}%</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">환율 (USD/KRW)</div>
        <div class="kpi-value">{current_usd_krw:,.0f} 원</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='section-header'>내 보유주식</div>", unsafe_allow_html=True
)

# 하단 종목 카드 배치
for data in all_stock_data:
    profit_class = "profit-pos" if data["profit_rate"] >= 0 else "profit-neg"
    avg_price_display = (
        f"${data['avg_price']:,.2f}"
        if data["currency"] == "USD"
        else f"{data['avg_price']:,.0f}원"
    )

    st.markdown(
        f"""
    <div class="stock-card">
        <div class="card-top">
            <div class="stock-name-area">
                <div class="company-logo">{data['logo_char']}</div>
                <div>
                    <div class="company-name">{data['name']}</div>
                    <div class="company-meta">{data['category']} · {data['ticker']}</div>
                </div>
            </div>
            <div class="card-price-area">
                <div class="current-price {profit_class}">{data['current_price_display']}</div>
                <div class="company-meta {profit_class}">{data['profit_rate']:.2f}%</div>
            </div>
        </div>
        <div class="card-bottom-grid">
            <div>
                <div class="info-label">보유수량</div>
                <div class="info-value">{data['shares']:.3f}주</div>
            </div>
            <div>
                <div class="info-label">평균단가</div>
                <div class="info-value">{avg_price_display}</div>
            </div>
            <div>
                <div class="info-label">평가손익</div>
                <div class="info-value {profit_class}">{data['profit_krw']:,.0f}원</div>
            </div>
            <div>
                <div class="info-label">평가금액</div>
                <div class="info-value">{data['current_val_krw']:,.0f}원</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

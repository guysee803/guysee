from datetime import datetime, timezone, timedelta
import pandas as pd
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V4 - 계좌별 보기 & 상세정보",
    page_icon="📈",
    layout="wide",
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

    .kpi-container {
        display: flex;
        gap: 20px;
        margin-bottom: 25px;
    }
    
    .kpi-card {
        flex: 1;
        background-color: #161b22;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border: 1px solid #2a323e;
    }

    .kpi-label {
        color: #a0aab5;
        font-size: 0.85rem;
        margin-bottom: 6px;
    }
    
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
    }

    .kpi-sub-value {
        color: #a0aab5;
        font-size: 0.85rem;
        margin-top: 4px;
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
        gap: 12px;
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
        font-size: 1.15rem;
        font-weight: 600;
        line-height: 1.2;
    }

    .company-meta {
        color: #a0aab5;
        font-size: 0.8rem;
        font-weight: 300;
    }

    .card-price-area {
        text-align: right;
    }

    .current-price {
        font-size: 1.3rem;
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
        font-size: 0.72rem;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .info-value {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    div[data-testid="stDataFrame"], div[data-testid="stTable"], header {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📂 전체 14개 종목 데이터 (요청하신 순서 반영)
# ---------------------------------------------------------
portfolio_data = [
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
        "category": "토스",
        "name": "SK스퀘어",
        "ticker": "402340.KS",
        "shares": 2,
        "avg_price": 1990000,
        "currency": "KRW",
        "logo": "S",
    },
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
        "name": "TIGER 200",
        "ticker": "102110.KS",
        "shares": 1,
        "avg_price": 100995,
        "currency": "KRW",
        "logo": "T",
    },
    {
        "category": "카카오페이",
        "name": "KODEX 200",
        "ticker": "069500.KS",
        "shares": 1,
        "avg_price": 101155,
        "currency": "KRW",
        "logo": "K",
    },
    {
        "category": "카카오페이",
        "name": "KODEX 코스닥150",
        "ticker": "229200.KS",
        "shares": 1,
        "avg_price": 20100,
        "currency": "KRW",
        "logo": "K",
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
        "name": "NVDL",
        "ticker": "NVDL",
        "shares": 4.23,
        "avg_price": 29.06,
        "currency": "USD",
        "logo": "N",
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
        "category": "카카오페이(ISA)",
        "name": "TIGER 미국배당다우존스타겟커버드콜1호",
        "ticker": "476970.KS",
        "shares": 13,
        "avg_price": 13506,
        "currency": "KRW",
        "logo": "T",
    },
    {
        "category": "카카오페이",
        "name": "PLUS 고배당주",
        "ticker": "294230.KS",
        "shares": 5,
        "avg_price": 26627,
        "currency": "KRW",
        "logo": "P",
    },
    {
        "category": "토스",
        "name": "크리에이트 엔터프라이즈",
        "ticker": "CRE8",
        "shares": 15,
        "avg_price": 4.48,
        "currency": "USD",
        "logo": "C",
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
        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            high_price = hist["High"].iloc[-1]
            low_price = hist["Low"].iloc[-1]
        else:
            current_price = item["avg_price"]
            high_price = item["avg_price"]
            low_price = item["avg_price"]
    except:
        current_price = item["avg_price"]
        high_price = item["avg_price"]
        low_price = item["avg_price"]

    if item["currency"] == "USD":
        invest_krw = item["avg_price"] * item["shares"] * exchange_rate
        current_val_krw = current_price * item["shares"] * exchange_rate
        current_price_display = f"${current_price:,.2f}"
        high_low_display = f"${low_price:,.2f} ~ ${high_price:,.2f}"
    else:
        invest_krw = item["avg_price"] * item["shares"]
        current_val_krw = current_price * item["shares"]
        current_price_display = f"{current_price:,.0f}원"
        high_low_display = f"{low_price:,.0f} ~ {high_price:,.0f}원"

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
        "high_low_display": high_low_display,
        "invest_krw": invest_krw,
        "current_val_krw": current_val_krw,
        "profit_krw": profit_krw,
        "profit_rate": profit_rate,
    }


# ---------------------------------------------------------
# 🖥️ 화면 렌더링 (KST 및 UTC 시간 분리 표기)
# ---------------------------------------------------------

st.title("석의 주식창")

# 한국 시간(KST, UTC+9)과 협정 세계시(UTC) 생성
kst = timezone(timedelta(hours=9))
utc = timezone.utc

time_kst = datetime.now(kst).strftime("%Y년 %m월 %d일 (%a) %H:%M")
time_utc = datetime.now(utc).strftime("%Y년 %m월 %d일 (%a) %H:%M")

st.markdown(
    f"""
<div class='main-subtitle'>
    🇰🇷 <b>한국 시간 (KST):</b> {time_kst} &nbsp;&nbsp;|&nbsp;&nbsp; 🌍 <b>협정 세계시 (UTC):</b> {time_utc} <br>
    <span style="color: #a0aab5; font-size: 0.9rem;">실시간 시세 및 고저가 반영 중</span>
</div>
""",
    unsafe_allow_html=True,
)

# 데이터 계산
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

# 상단 요약 카드 (전체 기준)
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

# ---------------------------------------------------------
# 📑 계좌별 탭 메뉴 (전체 보기 / 토스 / 카카오페이)
# ---------------------------------------------------------
tab_all, tab_toss, tab_kakao = st.tabs(
    ["📊 전체 보기", "💳 토스 계좌", "💬 카카오페이 계좌"]
)


def render_stock_cards(data_list):
    for data in data_list:
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
                    <div class="info-label">보유수량 / 평단</div>
                    <div class="info-value">{data['shares']:.3f}주 / {avg_price_display}</div>
                </div>
                <div>
                    <div class="info-label">당일 최저 ~ 최고가</div>
                    <div class="info-value" style="font-size: 0.9rem;">{data['high_low_display']}</div>
                </div>
                <div>
                    <div class="info-label">평가손익</div>
                    <div class="info-value {profit_class}">{data['profit_krw']:,.0f}원</div>
                </div>
                <div>
                    <div class="info-label">평가금액 (종가기준)</div>
                    <div class="info-value">{data['current_val_krw']:,.0f}원</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


with tab_all:
    render_stock_cards(all_stock_data)

with tab_toss:
    toss_data = [
        d
        for d in all_stock_data
        if d["name"] in ["SK하이닉스", "SK스퀘어", "크리에이트 엔터프라이즈"]
    ]
    render_stock_cards(toss_data)

with tab_kakao:
    kakao_data = [
        d
        for d in all_stock_data
        if d["name"] not in ["SK하이닉스", "SK스퀘어", "크리에이트 엔터프라이즈"]
    ]
    render_stock_cards(kakao_data)

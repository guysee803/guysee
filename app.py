import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V3 - 투자원금 중심", page_icon="📈", layout="wide"
)

# ---------------------------------------------------------
# 🎨 고급 CSS 스타일링 (더욱 세련된 다크 모드 디자인)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 전체 배경색 및 폰트 */
    .stApp {
        background-color: #0e1117; /* 진한 다크 네이비 */
        color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    /* 메인 헤더 제목 */
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 부제목 (날짜) */
    .main-subtitle {
        color: #a0aab5;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* 섹션 헤더 (내 보유주식) */
    .section-header {
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 2.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2a323e;
        padding-bottom: 10px;
    }

    /* ---------------------------------------------------------
       📊 상단 요약 지표 카드 (KPI Cards) 스타일
       --------------------------------------------------------- */
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
        transition: transform 0.3s;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
    }

    .kpi-label {
        color: #a0aab5;
        font-size: 0.9rem;
        font-weight: 400;
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

    /* ---------------------------------------------------------
       📈 하단 개별 주식 카드 스타일
       --------------------------------------------------------- */
    .stock-card {
        background-color: #161b22;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        border: 1px solid #2a323e;
        transition: transform 0.2s, border-color 0.2s;
    }
    
    .stock-card:hover {
        transform: translateY(-3px);
        border-color: #4a5568; /* 호버 시 테두리 색 변경 */
    }

    /* 카드 상단 (종목명, 로고, 현재가) */
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
        object-fit: cover;
        background-color: #2a323e; /* 로고 없을 때 배경 */
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
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

    /* 수익률 색상 */
    .profit-pos {
        color: #ef476f !important; /* 레드 */
    }
    .profit-neg {
        color: #118ab2 !important; /* 블루 */
    }

    /* 카드 하단 (상세 정보 그리드) */
    .card-bottom-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        border-top: 1px solid #2a323e;
        padding-top: 15px;
    }
    
    .info-box {
        text-align: left;
    }

    .info-label {
        color: #a0aab5;
        font-size: 0.75rem;
        font-weight: 300;
        margin-bottom: 4px;
        text-transform: uppercase; /* 대문자 변환 */
        letter-spacing: 0.05em;
    }

    .info-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: #ffffff;
    }
    
    /* Streamlit 기본 숨기기 */
    div[data-testid="stDataFrame"], div[data-testid="stTable"], header {
        display: none;
    }
    
    /* 로딩 스피너 색상 */
    .stSpinner > div > div {
        border-top-color: #f0a500 !important;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 📂 데이터 및 로직 영역
# ---------------------------------------------------------

# 보유 종목 리스트 (업데이트된 수량 및 티커 반영)
portfolio_data = [
    {"category": "카카오페이", "name": "삼성전자", "ticker": "005930.KS", "shares": 20, "avg_price": 126052, "currency": "KRW", "logo": "삼"},
    {"category": "토스", "name": "SK하이닉스", "ticker": "000660.KS", "shares": 2, "avg_price": 2545000, "currency": "KRW", "logo": "S"},
    {"category": "토스", "name": "SK스퀘어", "ticker": "402340.KS", "shares": 2, "avg_price": 1990000, "currency": "KRW", "logo": "S"},
    {"category": "카카오페이", "name": "엔비디아 (종합계좌)", "ticker": "NVDA", "shares": 2.748, "avg_price": 192.28, "currency": "USD", "logo": "N"},
    {"category": "카카오페이", "name": "두산에너빌리티", "ticker": "034020.KS", "shares": 10, "avg_price": 82950, "currency": "KRW", "logo": "두"},
    {"category": "카카오페이", "name": "우리금융지주", "ticker": "316140.KS", "shares": 10, "avg_price": 32015, "currency": "KRW", "logo": "우"},
    {"category": "카카오페이", "name": "엔비디아 (RIA계좌)", "ticker": "NVDA", "shares": 1, "avg_price": 182.23, "currency": "USD", "logo": "N"},
    {"category": "카카오페이", "name": "NVDL", "ticker": "NVDL", "shares": 4.23, "avg_price": 29.06, "currency": "USD", "logo": "N"},
]

# 원/달러 환율 가져오기 (오류 방지 추가)
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        ticker = yf.Ticker("USDCKR=X")
        data = ticker.history(period="1d")
        return data["Close"].iloc[-1]
    except Exception as e:
        # 환율 정보 못 가져올 경우 기본값 (최신 근사치)
        st.warning(f"환율 정보를 가져오지 못해 기본값(1345원)을 사용합니다. 오류: {e}")
        return 1345.0

current_usd_krw = get_exchange_rate()

# 데이터 계산 함수
def calculate_stock(item, exchange_rate):
    ticker = yf.Ticker(item["ticker"])
    try:
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
        else:
            current_price = item["avg_price"] # 데이터 없으면 매수가로 간주
    except:
        current_price = item["avg_price"]
        
    # 평가금액 및 손익 계산 (KRW 기준)
    if item["currency"] == "USD":
        # 투자원금
        invest_krw = item["avg_price"] * item["shares"] * exchange_rate
        # 평가금액
        current_val_krw = current_price * item["shares"] * exchange_rate
        # 현재가 표시용 (USD)
        current_price_display = f"${current_price:,.2f}"
    else:
        invest_krw = item["avg_price"] * item["shares"]
        current_val_krw = current_price * item["shares"]
        current_price_display = f"{current_price:,.0f}원"

    # 평가손익 및 수익률
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
        "profit_rate": profit_rate
    }

# ---------------------------------------------------------
# 🖥️ 화면 구성 (대시보드 렌더링)
# ---------------------------------------------------------

# 1. 상단 헤더
st.title("석의 주식창")
# 현재 날짜 및 시간 표시
current_time = datetime.now().strftime("%Y년 %m월 %d일 (%a) %H:%M")
st.markdown(f"<div class='main-subtitle'>{current_time} · 실시간 시세 반영 중</div>", unsafe_allow_html=True)

# 2. 데이터 처리 및 요약 지표 계산
all_stock_data = []
total_invest = 0
total_current_val = 0

with st.spinner("실시간 시세 데이터를 불러오는 중입니다..."):
    for item in portfolio_data:
        data = calculate_stock(item, current_usd_krw)
        all_stock_data.append(data)
        total_invest += data["invest_krw"]
        total_current_val += data["current_val_krw"]

# 총 평가손익 및 수익률 계산
total_profit = total_current_val - total_invest
total_profit_rate = (total_profit / total_invest * 100) if total_invest != 0 else 0
profit_class_total = "profit-pos" if total_profit >= 0 else "profit-neg"

# 3. 상단 핵심 요약 카드 (KPI) 영역
st.markdown(f"""
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
""", unsafe_allow_html=True)

# 4. 보유주식 섹션 제목
st.markdown("<div class='section-header'>내 보유주식</div>", unsafe_allow_html=True)

# 5. 하단 개별 종목 카드 목록
# 한 줄에 2개씩 카드를 배치하기 위해 컬럼 사용
col1, col2 = st.columns(2)

for i, data in enumerate(all_stock_data):
    profit_class = "profit-pos" if data['profit_rate'] >= 0 else "profit-neg"
    avg_price_display = f"${data['avg_price']:,.2f}" if data['currency'] == "USD" else f"{data['avg_price']:,.0f}원"
    
    # 카드 HTML 구성 (이미지 디자인을 최대한 반영)
    card_html = f"""
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
            <div class="info-box">
                <div class="

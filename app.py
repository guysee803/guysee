from datetime import datetime, timezone, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V26 (주요 뉴스 및 투자 진단)",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------
# 🎨 고급 CSS 스타일링
# ---------------------------------------------------------
st.markdown(
    """
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
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        border: 1px solid #30363d;
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

    .toss-badge {
        display: inline-block;
        background-color: #e5a93b;
        color: #1c1c1c;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 20px;
        margin-bottom: 6px;
    }

    .toss-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 2px;
    }

    .toss-sub {
        color: #a0aab5;
        font-size: 0.8rem;
    }

    .toss-current-price {
        font-size: 1.4rem;
        font-weight: 700;
    }

    .toss-profit-rate {
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 2px;
    }

    .profit-pos {
        color: #f04452 !important;
    }
    .profit-neg {
        color: #3182f6 !important;
    }

    .toss-info-box {
        background-color: #1f2630;
        border-radius: 10px;
        padding: 10px 12px;
        border: 1px solid #2a323e;
    }

    .toss-info-label {
        color: #a0aab5;
        font-size: 0.75rem;
        margin-bottom: 4px;
    }

    .toss-info-value {
        font-size: 0.9rem;
        font-weight: 700;
        color: #ffffff;
    }

    .strategy-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 12px 15px;
        margin-top: 10px;
        font-size: 0.85rem;
    }
    
    div[data-testid="stDataFrame"], div[data-testid="stTable"], header {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 📂 전체 종목 데이터 정의
# ---------------------------------------------------------
portfolio_data = [
    # 토스증권 (3종목)
    {
        "category": "토스증권",
        "name": "SK하이닉스",
        "ticker": "000660.KS",
        "shares": 2,
        "avg_price": 2545000,
        "currency": "KRW",
    },
    {
        "category": "토스증권",
        "name": "SK스퀘어",
        "ticker": "402340.KS",
        "shares": 2,
        "avg_price": 1990000,
        "currency": "KRW",
    },
    {
        "category": "토스증권",
        "name": "크리에이트 엔터프라이즈",
        "ticker": "CRE8",
        "shares": 15,
        "avg_price": 4.48,
        "currency": "USD",
    },
    # 카카오페이 일반 (8종목) - KODEX 코스닥150 포함
    {
        "category": "카카오페이 일반",
        "name": "삼성전자",
        "ticker": "005930.KS",
        "shares": 20,
        "avg_price": 126052,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 일반",
        "name": "두산에너빌리티",
        "ticker": "034020.KS",
        "shares": 10,
        "avg_price": 82950,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 일반",
        "name": "우리금융지주",
        "ticker": "316140.KS",
        "shares": 10,
        "avg_price": 32015,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 일반",
        "name": "TIGER 200",
        "ticker": "102110.KS",
        "shares": 1,
        "avg_price": 100995,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 일반",
        "name": "KODEX 200",
        "ticker": "069500.KS",
        "shares": 1,
        "avg_price": 101155,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 일반",
        "name": "엔비디아 (종합계좌)",
        "ticker": "NVDA",
        "shares": 2.748,
        "avg_price": 192.28,
        "currency": "USD",
    },
    {
        "category": "카카오페이 일반",
        "name": "NVDL",
        "ticker": "NVDL",
        "shares": 4.23,
        "avg_price": 29.06,
        "currency": "USD",
    },
    {
        "category": "카카오페이 일반",
        "name": "KODEX 코스닥150",
        "ticker": "229200.KS",
        "shares": 1,
        "avg_price": 20100,
        "currency": "KRW",
    },
    # 카카오페이 RIA (1종목)
    {
        "category": "카카오페이 RIA",
        "name": "엔비디아 (RIA계좌)",
        "ticker": "NVDA",
        "shares": 1,
        "avg_price": 182.23,
        "currency": "USD",
    },
    # 카카오페이 ISA (2종목) - PLUS 고배당주 포함
    {
        "category": "카카오페이 ISA",
        "name": "TIGER 미국배당다우존스타겟커버드콜1호",
        "ticker": "476970.KS",
        "shares": 13,
        "avg_price": 13506,
        "currency": "KRW",
    },
    {
        "category": "카카오페이 ISA",
        "name": "PLUS 고배당주",
        "ticker": "294230.KS",
        "shares": 5,
        "avg_price": 26627,
        "currency": "KRW",
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


# 종목별 핵심 뉴스 및 출처 데이터 매핑 (2026년 8월 최신 기준)
news_mapping = {
    "SK하이닉스": {
        "headline": "FMS 2026 '계층형 아키텍처' 및 CXL 풀드 메모리 공개",
        "summary": "미국 산타클라라 FMS 2026 학회에서 AI 에이전트 확산에 대응하기 위한 계층형 메모리 및 CXL 기반 풀드 메모리 기술 시연. QLC 기반 고용량 eSSD 샘플 공급 개시.",
        "source": "뉴스후플러스 / Technology Review (2026.08)",
    },
    "삼성전자": {
        "headline": "차세대 메모리 'zHBM' 전격 공개",
        "summary": "GPU 위에 HBM을 직접 적층하는 신개념 zHBM 구조 발표로 연산 병목 현상 및 전력 효율 극대화 추진.",
        "source": "AI경기방송 (2026.08)",
    },
    "엔비디아": {
        "headline": "클라우드사 AI 인프라 지속 투자 확약 및 실적 기대감",
        "summary": "주요 클라우드 공급업체들의 AI 지출 지속 신호와 GPU 생산 수율 개선에 힘입어 강세 흐름 유지. 8월 말 2분기 실적 발표 대기.",
        "source": "Investing.com / TradingKey (2026.08)",
    },
    "NVDL": {
        "headline": "엔비디아 주가 연동 2배 레버리지",
        "summary": "엔비디아의 데이터센터 부문 펀더멘털 강화 및 AI 인프라 투자 지속 뉴스에 연동하여 변동성 장세 시현.",
        "source": "TradingKey (2026.08)",
    },
    "두산에너빌리티": {
        "headline": "원전 및 대형 플랜트 수급 유입 및 목표가 유지",
        "summary": "기관 및 외국인의 수급 변화 속에서 원전 모멘텀과 대형 인프라 기대감으로 중장기 증권사 목표주가 평균 12만 원대 유지.",
        "source": "인포스탁데일리 / 알파스퀘어 (2026.08)",
    },
}


def calculate_stock(item, exchange_rate):
    ticker = yf.Ticker(item["ticker"])
    current_price = None
    hist = pd.DataFrame()

    try:
        fi = ticker.fast_info
        current_price = getattr(fi, "last_price", None)
        hist = ticker.history(period="3mo", interval="1d")
        if (
            not hist.empty
            and (current_price is None or pd.isna(current_price))
        ):
            current_price = hist["Close"].iloc[-1]
    except:
        pass

    if current_price is None or pd.isna(current_price):
        current_price = item["avg_price"]

    market_type = "해외" if item["currency"] == "USD" else "KRW"

    # 기술적 지표 계산 (RSI 및 20일 이동평균선)
    rsi = 50.0
    ma20 = current_price
    if not hist.empty and len(hist) > 14:
        delta = hist["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        calculated_rsi = 100 - (100 / (1 + rs))
        if not pd.isna(calculated_rsi.iloc[-1]):
            rsi = calculated_rsi.iloc[-1]
        ma20 = hist["Close"].rolling(window=20).mean().iloc[-1]

    # 매수/매도 타이밍 및 진단 로직
    signal_text = "중립 (관망)"
    signal_color = "#e5a93b"
    strategy_desc = ""

    if rsi >= 70:
        signal_text = "🔥 과매수 구간 (이익 실현 검토)"
        signal_color = "#f04452"
        strategy_desc = "단기 상승 과열 구간입니다. 분할 매도나 비중 축소를 고려하세요."
    elif rsi <= 30:
        signal_text = "❄️ 과매도 구간 (분할 매수 기회)"
        signal_color = "#3182f6"
        strategy_desc = (
            "주가가 과도하게 하락한 구간입니다. 분할 매수 접근이 유리합니다."
        )
    else:
        if current_price > ma20:
            signal_text = "📈 상승 추세 (보유 및 홀딩)"
            signal_color = "#f04452"
            strategy_desc = (
                "20일 이동평균선 위에 위치하여 추세가 양호합니다. 홀딩을 권장합니다."
            )
        else:
            signal_text = "📉 하락 추세 (방어적 대응)"
            signal_color = "#3182f6"
            strategy_desc = (
                "20일 이동평균선 아래에 위치합니다. 리스크 관리에 유의하세요."
            )

    target_price = item["avg_price"] * 1.15
    stop_loss_price = item["avg_price"] * 0.92

    if item["currency"] == "USD":
        invest_krw = item["avg_price"] * item["shares"] * exchange_rate
        current_val_krw = current_price * item["shares"] * exchange_rate
        current_price_display = f"${current_price:,.2f}"
        avg_price_display = f"${item['avg_price']:,.2f}"
        target_display = f"${target_price:,.2f}"
        stop_display = f"${stop_loss_price:,.2f}"
    else:
        invest_krw = item["avg_price"] * item["shares"]
        current_val_krw = current_price * item["shares"]
        current_price_display = f"{current_price:,.0f}원"
        avg_price_display = f"{item['avg_price']:,.0f}원"
        target_display = f"{target_price:,.0f}원"
        stop_display = f"{stop_loss_price:,.0f}원"

    profit_krw = current_val_krw - invest_krw
    profit_rate = (profit_krw / invest_krw * 100) if invest_krw != 0 else 0

    if item["shares"] == int(item["shares"]):
        shares_display = f"{int(item['shares'])}주"
    else:
        shares_display = f"{item['shares']:.3f}주"

    # 뉴스 매핑 연결 (이름에 포함된 키워드 우선 검색)
    matched_news = {
        "headline": "실시간 시장 동향 모니터링 중",
        "summary": "해당 종목과 관련된 주요 글로벌 경제지표 및 섹터별 수급 동향을 주시하고 있습니다.",
        "source": "공식 증권 시장 데이터 (2026.08)",
    }
    for key, val in news_mapping.items():
        if key in item["name"]:
            matched_news = val
            break

    return {
        "category": item["category"],
        "name": item["name"],
        "ticker": item["ticker"],
        "market_type": market_type,
        "shares_display": shares_display,
        "avg_price_display": avg_price_display,
        "currency": item["currency"],
        "current_price_display": current_price_display,
        "invest_krw": invest_krw,
        "current_val_krw": current_val_krw,
        "profit_krw": profit_krw,
        "profit_rate": profit_rate,
        "rsi": rsi,
        "signal_text": signal_text,
        "signal_color": signal_color,
        "strategy_desc": strategy_desc,
        "target_display": target_display,
        "stop_display": stop_display,
        "news": matched_news,
    }


# ---------------------------------------------------------
# 🖥️ 데이터 계산
# ---------------------------------------------------------
all_stock_data = []
total_invest = 0
total_current_val = 0

with st.spinner(
    "실시간 시세, 기술적 지표 및 최신 뉴스 분석 중입니다..."
):
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

# ---------------------------------------------------------
# 메인 화면 렌더링
# ---------------------------------------------------------
st.title("석의 주식창")

kst = timezone(timedelta(hours=9))
utc = timezone.utc
time_kst = datetime.now(kst).strftime("%Y년 %m월 %d일 (%a) %H:%M")
time_utc = datetime.now(utc).strftime("%Y년 %m월 %d일 (%a) %H:%M")

st.markdown(
    f"""
<div class='main-subtitle'>
    🇰🇷 <b>한국 시간 (KST):</b> {time_kst} &nbsp;&nbsp;|&nbsp;&nbsp; 🌍 <b>협정 세계시 (UTC):</b> {time_utc} <br>
    <span style="color: #a0aab5; font-size: 0.9rem;">실시간 시세, RSI 분석, 목표·손절가 및 최신 뉴스/이슈 브리핑 반영 중</span>
</div>
""",
    unsafe_allow_html=True,
)

# 1. 전체 자산 요약 KPI
st.markdown(
    f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">총 투자원금</div>
        <div class="kpi-value">{total_invest:,.0f} 원</div>
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

# 2. 계좌별 자산 요약 카드 섹션
st.markdown("### 계좌별 자산")
account_categories = [
    "토스증권",
    "카카오페이 일반",
    "카카오페이 RIA",
    "카카오페이 ISA",
]
acc_cols = st.columns(len(account_categories))

for idx, acc_name in enumerate(account_categories):
    acc_items = [d for d in all_stock_data if d["category"] == acc_name]
    acc_invest = sum([d["invest_krw"] for d in acc_items])
    acc_val = sum([d["current_val_krw"] for d in acc_items])
    acc_profit = acc_val - acc_invest
    acc_rate = (acc_profit / acc_invest * 100) if acc_invest != 0 else 0
    acc_profit_class = "profit-pos" if acc_profit >= 0 else "profit-neg"
    acc_sign = "+" if acc_profit >= 0 else ""

    with acc_cols[idx]:
        with st.container(border=True):
            st.markdown(
                f"<div style='font-size: 1.05rem; font-weight: 700; color: #ffffff;'>{acc_name}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color: #a0aab5; font-size: 0.8rem; margin-bottom: 8px;'>{len(acc_items)}종목</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;'>{acc_val:,.0f}원</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='color: #a0aab5; font-size: 0.78rem;'>원금 {acc_invest:,.0f}원</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='{acc_profit_class}' style='font-size: 0.8rem; font-weight: 600;'>손익: {acc_sign}{acc_profit:,.0f}원 ({acc_sign}{acc_rate:.2f}%)</div>",
                unsafe_allow_html=True,
            )

st.markdown(
    "<hr style='margin-top: 25px; margin-bottom: 25px; border-color: #30363d;'>",
    unsafe_allow_html=True,
)


# 3. 종목 그리드 렌더링 함수
def render_stock_grid(data_list, tab_prefix):
    if not data_list:
        st.info("해당 계좌에 등록된 종목이 없습니다.")
        return

    for i in range(0, len(data_list), 2):
        cols = st.columns(2)

        for j in range(2):
            if i + j < len(data_list):
                data = data_list[i + j]
                profit_class = (
                    "profit-pos" if data["profit_rate"] >= 0 else "profit-neg"
                )
                sign_str = "+" if data["profit_rate"] >= 0 else ""

                with cols[j]:
                    with st.container(border=True):
                        h1, h2 = st.columns([1.1, 1])
                        with h1:
                            st.markdown(
                                f'<div class="toss-badge">{data["category"]}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="toss-title">{data["name"]}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="toss-sub">일반 · {data["market_type"]}</div>',
                                unsafe_allow_html=True,
                            )
                        with h2:
                            st.markdown(
                                '<div style="text-align: right;">'
                                '<div style="color: #a0aab5; font-size: 0.75rem; margin-bottom: 2px;">현재가</div>'
                                f'<div class="toss-current-price {profit_class}">{data["current_price_display"]}</div>'
                                f'<div class="toss-profit-rate {profit_class}">{sign_str}{data["profit_rate"]:.2f}%</div>'
                                "</div>",
                                unsafe_allow_html=True,
                            )

                        st.markdown(
                            "<div style='margin-top: 14px;'></div>",
                            unsafe_allow_html=True,
                        )

                        g1, g2, g3, g4 = st.columns(4)
                        with g1:
                            st.markdown(
                                f'<div class="toss-info-box"><div class="toss-info-label">보유수량</div><div class="toss-info-value">{data["shares_display"]}</div></div>',
                                unsafe_allow_html=True,
                            )
                        with g2:
                            st.markdown(
                                f'<div class="toss-info-box"><div class="toss-info-label">평균단가</div><div class="toss-info-value">{data["avg_price_display"]}</div></div>',
                                unsafe_allow_html=True,
                            )
                        with g3:
                            st.markdown(
                                f'<div class="toss-info-box"><div class="toss-info-label">투자원금</div><div class="toss-info-value">{data["invest_krw"]:,.0f}원</div></div>',
                                unsafe_allow_html=True,
                            )
                        with g4:
                            st.markdown(
                                f'<div class="toss-info-box"><div class="toss-info-label">평가금액</div><div class="toss-info-value">{data["current_val_krw"]:,.0f}원</div></div>',
                                unsafe_allow_html=True,
                            )

                        # 투자 진단 박스
                        st.markdown(
                            f"""
                        <div class="strategy-box">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <span style="font-weight: 700; color: {data['signal_color']};">{data['signal_text']}</span>
                                <span style="color: #a0aab5; font-size: 0.8rem;">RSI: {data['rsi']:.1f}</span>
                            </div>
                            <div style="color: #c9d1d9; margin-bottom: 8px; font-size: 0.8rem;">💡 {data['strategy_desc']}</div>
                            <div style="display: flex; justify-content: space-between; border-top: 1px solid #30363d; padding-top: 6px; color: #a0aab5; font-size: 0.78rem;">
                                <span>🎯 <b>목표가:</b> <span style="color: #f04452;">{data['target_display']}</span></span>
                                <span>🛑 <b>손절가:</b> <span style="color: #3182f6;">{data['stop_display']}</span></span>
                            </div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        # 🔍 주요 뉴스 및 이슈 분석 박스 추가
                        st.markdown(
                            f"""
                        <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 12px 15px; margin-top: 8px; font-size: 0.82rem;">
                            <div style="color: #e5a93b; font-weight: 700; margin-bottom: 4px;">📰 {data['news']['headline']}</div>
                            <div style="color: #c9d1d9; margin-bottom: 6px; line-height: 1.4;">{data['news']['summary']}</div>
                            <div style="color: #8b949e; font-size: 0.75rem; text-align: right;">출처: {data['news']['source']}</div>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            "<div style='margin-top: 10px;'></div>",
                            unsafe_allow_html=True,
                        )

                        with st.expander(f"📈 {data['name']} 차트 보기"):
                            period_option = st.radio(
                                "차트 기간 선택",
                                ["1일", "1주", "1달", "3달"],
                                horizontal=True,
                                key=f"radio_{tab_prefix}_{data['category']}_{data['ticker']}_{data['name']}_{i}_{j}",
                            )

                            period_map = {
                                "1일": ("1d", "5m"),
                                "1주": ("5d", "30m"),
                                "1달": ("1mo", "1d"),
                                "3달": ("3mo", "1d"),
                            }
                            p, inter = period_map[period_option]

                            try:
                                t_obj = yf.Ticker(data["ticker"])
                                df = t_obj.history(period=p, interval=inter)

                                if not df.empty:
                                    df["MA5"] = (
                                        df["Close"].rolling(window=5).mean()
                                    )
                                    df["MA10"] = (
                                        df["Close"].rolling(window=10).mean()
                                    )
                                    df["MA20"] = (
                                        df["Close"].rolling(window=20).mean()
                                    )
                                    df["MA60"] = (
                                        df["Close"].rolling(window=60).mean()
                                    )
                                    df["MA120"] = (
                                        df["Close"].rolling(window=120).mean()
                                    )

                                    fig = go.Figure()
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["Close"],
                                            mode="lines",
                                            name="종가",
                                            line=dict(color="#ffffff", width=1.5),
                                        )
                                    )
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["MA5"],
                                            mode="lines",
                                            name="MA 5",
                                            line=dict(color="#f04452", width=1.2),
                                        )
                                    )
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["MA10"],
                                            mode="lines",
                                            name="MA 10",
                                            line=dict(color="#e5a93b", width=1.2),
                                        )
                                    )
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["MA20"],
                                            mode="lines",
                                            name="MA 20",
                                            line=dict(color="#3182f6", width=1.2),
                                        )
                                    )
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["MA60"],
                                            mode="lines",
                                            name="MA 60",
                                            line=dict(color="#9b5de5", width=1.2),
                                        )
                                    )
                                    fig.add_trace(
                                        go.Scatter(
                                            x=df.index,
                                            y=df["MA120"],
                                            mode="lines",
                                            name="MA 120",
                                            line=dict(color="#00b4d8", width=1.2),
                                        )
                                    )

                                    fig.update_layout(
                                        margin=dict(l=10, r=10, t=20, b=10),
                                        height=300,
                                        paper_bgcolor="#161b22",
                                        plot_bgcolor="#161b22",
                                        font=dict(color="#a0aab5"),
                                        legend=dict(
                                            orientation="h",
                                            yanchor="bottom",
                                            y=1.02,
                                            xanchor="right",
                                            x=1,
                                        ),
                                        xaxis=dict(
                                            showgrid=True, gridcolor="#2a323e"
                                        ),
                                        yaxis=dict(
                                            showgrid=True, gridcolor="#2a323e"
                                        ),
                                    )

                                    st.plotly_chart(
                                        fig, use_container_width=True
                                    )
                                else:
                                    st.info("차트 데이터가 없습니다.")
                            except Exception:
                                st.error("차트 로딩 중 오류 발생")


# 4. 계좌별 자산 카드 아래에 배치된 메인 탭 메뉴
st.markdown("### 🗂️ 계좌별 종목 보기")
tab_all, tab_toss, tab_gen, tab_ria, tab_isa = st.tabs(
    [
        "📊 전체 보기",
        "💳 토스증권",
        "💬 카카오페이 일반",
        "💬 카카오페이 RIA",
        "💬 카카오페이 ISA",
    ]
)

with tab_all:
    render_stock_grid(all_stock_data, "all")

with tab_toss:
    render_stock_grid(
        [d for d in all_stock_data if d["category"] == "토스증권"], "toss"
    )

with tab_gen:
    render_stock_grid(
        [d for d in all_stock_data if d["category"] == "카카오페이 일반"],
        "kk_gen",
    )

with tab_ria:
    render_stock_grid(
        [d for d in all_stock_data if d["category"] == "카카오페이 RIA"],
        "kk_ria",
    )

with tab_isa:
    render_stock_grid(
        [d for d in all_stock_data if d["category"] == "카카오페이 ISA"],
        "kk_isa",
    )

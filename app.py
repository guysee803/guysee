from datetime import datetime, timezone, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------
# 🌐 웹페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="석의 주식창 V7 - 다중 이동평균선 추가",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------
# 🎨 고급 CSS 스타일링 (토스앱 스타일 카드 디자인)
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

    /* 토스 스타일 주식 카드 */
    .toss-card {
        background-color: #161b22;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.25);
        border: 1px solid #2a323e;
    }
    
    .toss-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
    }

    .toss-badge {
        display: inline-block;
        background-color: #e5a93b;
        color: #1c1c1c;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 8px;
    }

    .toss-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }

    .toss-sub {
        color: #a0aab5;
        font-size: 0.85rem;
    }

    .toss-price-area {
        text-align: right;
    }

    .toss-price-label {
        color: #a0aab5;
        font-size: 0.8rem;
        margin-bottom: 2px;
    }

    .toss-current-price {
        font-size: 1.6rem;
        font-weight: 700;
    }

    .toss-profit-rate {
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 2px;
    }

    .profit-pos {
        color: #f04452 !important;
    }
    .profit-neg {
        color: #3182f6 !important;
    }

    /* 하단 4개 정보 박스 그리드 */
    .toss-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }

    .toss-info-box {
        background-color: #1f2630;
        border-radius: 14px;
        padding: 14px 16px;
    }

    .toss-info-label {
        color: #a0aab5;
        font-size: 0.8rem;
        margin-bottom: 6px;
    }

    .toss-info-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
    }
    
    div[data-testid="stDataFrame"], div[data-testid="stTable"], header {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 📂 전체 14개 종목 데이터
# ---------------------------------------------------------
portfolio_data = [
    {
        "category": "토스",
        "name": "SK하이닉스",
        "ticker": "000660.KS",
        "shares": 2,
        "avg_price": 2545000,
        "currency": "KRW",
    },
    {
        "category": "토스",
        "name": "SK스퀘어",
        "ticker": "402340.KS",
        "shares": 2,
        "avg_price": 1990000,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "삼성전자",
        "ticker": "005930.KS",
        "shares": 20,
        "avg_price": 126052,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "두산에너빌리티",
        "ticker": "034020.KS",
        "shares": 10,
        "avg_price": 82950,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "우리금융지주",
        "ticker": "316140.KS",
        "shares": 10,
        "avg_price": 32015,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "TIGER 200",
        "ticker": "102110.KS",
        "shares": 1,
        "avg_price": 100995,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "KODEX 200",
        "ticker": "069500.KS",
        "shares": 1,
        "avg_price": 101155,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "KODEX 코스닥150",
        "ticker": "229200.KS",
        "shares": 1,
        "avg_price": 20100,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "엔비디아 (종합계좌)",
        "ticker": "NVDA",
        "shares": 2.748,
        "avg_price": 192.28,
        "currency": "USD",
    },
    {
        "category": "카카오페이",
        "name": "NVDL",
        "ticker": "NVDL",
        "shares": 4.23,
        "avg_price": 29.06,
        "currency": "USD",
    },
    {
        "category": "카카오페이",
        "name": "엔비디아 (RIA계좌)",
        "ticker": "NVDA",
        "shares": 1,
        "avg_price": 182.23,
        "currency": "USD",
    },
    {
        "category": "카카오페이(ISA)",
        "name": "TIGER 미국배당다우존스타겟커버드콜1호",
        "ticker": "476970.KS",
        "shares": 13,
        "avg_price": 13506,
        "currency": "KRW",
    },
    {
        "category": "카카오페이",
        "name": "PLUS 고배당주",
        "ticker": "294230.KS",
        "shares": 5,
        "avg_price": 26627,
        "currency": "KRW",
    },
    {
        "category": "토스",
        "name": "크리에이트 엔터프라이즈",
        "ticker": "CRE8",
        "shares": 15,
        "avg_price": 4.48,
        "currency": "USD",
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
        fi = ticker.fast_info
        current_price = getattr(fi, "last_price", None)

        if not current_price:
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist["Close"].iloc[-1]
            else:
                current_price = item["avg_price"]
    except:
        current_price = item["avg_price"]

    if item["currency"] == "USD":
        invest_krw = item["avg_price"] * item["shares"] * exchange_rate
        current_val_krw = current_price * item["shares"] * exchange_rate
        current_price_display = f"${current_price:,.2f}"
        avg_price_display = f"${item['avg_price']:,.2f}"
    else:
        invest_krw = item["avg_price"] * item["shares"]
        current_val_krw = current_price * item["shares"]
        current_price_display = f"{current_price:,.0f}원"
        avg_price_display = f"{item['avg_price']:,.0f}원"

    profit_krw = current_val_krw - invest_krw
    profit_rate = (profit_krw / invest_krw * 100) if invest_krw != 0 else 0

    if item["shares"] == int(item["shares"]):
        shares_display = f"{int(item['shares'])}주"
    else:
        shares_display = f"{item['shares']:.3f}주"

    return {
        "category": item["category"],
        "name": item["name"],
        "ticker": item["ticker"],
        "shares_display": shares_display,
        "avg_price_display": avg_price_display,
        "currency": item["currency"],
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

kst = timezone(timedelta(hours=9))
utc = timezone.utc

time_kst = datetime.now(kst).strftime("%Y년 %m월 %d일 (%a) %H:%M")
time_utc = datetime.now(utc).strftime("%Y년 %m월 %d일 (%a) %H:%M")

st.markdown(
    f"""
<div class='main-subtitle'>
    🇰🇷 <b>한국 시간 (KST):</b> {time_kst} &nbsp;&nbsp;|&nbsp;&nbsp; 🌍 <b>협정 세계시 (UTC):</b> {time_utc} <br>
    <span style="color: #a0aab5; font-size: 0.9rem;">실시간 시세 및 5/10/20/60/120일 이동평균선 반영 중</span>
</div>
""",
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

tab_all, tab_toss, tab_kakao = st.tabs(
    ["📊 전체 보기", "💳 토스 계좌", "💬 카카오페이 계좌"]
)


def render_stock_cards(data_list):
    for data in data_list:
        profit_class = "profit-pos" if data["profit_rate"] >= 0 else "profit-neg"
        sign_str = "+" if data["profit_rate"] >= 0 else ""

        with st.expander(
            f"📌 {data['name']} - 현재가: {data['current_price_display']} ({sign_str}{data['profit_rate']:.2f}%)"
        ):
            st.markdown(
                f"""
            <div class="toss-card">
                <div class="toss-header">
                    <div>
                        <div class="toss-badge">{data['category']}</div>
                        <div class="toss-title">{data['name']}</div>
                        <div class="toss-sub">일반 · {data['ticker']}</div>
                    </div>
                    <div class="toss-price-area">
                        <div class="toss-price-label">현재가</div>
                        <div class="toss-current-price {profit_class}">{data['current_price_display']}</div>
                        <div class="toss-profit-rate {profit_class}">{sign_str}{data['profit_rate']:.2f}%</div>
                    </div>
                </div>
                
                <div class="toss-grid">
                    <div class="toss-info-box">
                        <div class="toss-info-label">보유수량</div>
                        <div class="toss-info-value">{data['shares_display']}</div>
                    </div>
                    <div class="toss-info-box">
                        <div class="toss-info-label">평균단가</div>
                        <div class="toss-info-value">{data['avg_price_display']}</div>
                    </div>
                    <div class="toss-info-box">
                        <div class="toss-info-label">투자원금</div>
                        <div class="toss-info-value">{data['invest_krw']:,.0f}원</div>
                    </div>
                    <div class="toss-info-box">
                        <div class="toss-info-label">평가금액</div>
                        <div class="toss-info-value">{data['current_val_krw']:,.0f}원</div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            period_option = st.radio(
                "차트 기간 선택",
                ["1일", "1주", "1달", "3달"],
                horizontal=True,
                key=f"radio_{data['category']}_{data['ticker']}_{data['name']}",
            )

            period_map = {
                "1일": ("1d", "5m"),
                "1주": ("5d", "30m"),
                "1달": ("1mo", "1d"),
                "3달": ("3mo", "1d"),
            }
            p, i = period_map[period_option]

            try:
                t_obj = yf.Ticker(data["ticker"])
                df = t_obj.history(period=p, interval=i)

                if not df.empty:
                    # 5일, 10일, 20일, 60일, 120일 이동평균선 계산
                    df["MA5"] = df["Close"].rolling(window=5).mean()
                    df["MA10"] = df["Close"].rolling(window=10).mean()
                    df["MA20"] = df["Close"].rolling(window=20).mean()
                    df["MA60"] = df["Close"].rolling(window=60).mean()
                    df["MA120"] = df["Close"].rolling(window=120).mean()

                    # Plotly 차트 생성
                    fig = go.Figure()

                    # 종가 라인
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["Close"],
                            mode="lines",
                            name="종가",
                            line=dict(color="#ffffff", width=1.5),
                        )
                    )

                    # 5일선
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["MA5"],
                            mode="lines",
                            name="MA 5",
                            line=dict(color="#f04452", width=1.2),
                        )
                    )

                    # 10일선
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["MA10"],
                            mode="lines",
                            name="MA 10",
                            line=dict(color="#e5a93b", width=1.2),
                        )
                    )

                    # 20일선
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["MA20"],
                            mode="lines",
                            name="MA 20",
                            line=dict(color="#3182f6", width=1.2),
                        )
                    )

                    # 60일선
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["MA60"],
                            mode="lines",
                            name="MA 60",
                            line=dict(color="#9b5de5", width=1.2),
                        )
                    )

                    # 120일선
                    fig.add_trace(
                        go.Scatter(
                            x=df.index,
                            y=df["MA120"],
                            mode="lines",
                            name="MA 120",
                            line=dict(color="#00b4d8", width=1.2),
                        )
                    )

                    # 차트 레이아웃 디자인 설정 (다크모드 맞춤)
                    fig.update_layout(
                        margin=dict(l=10, r=10, t=20, b=10),
                        height=320,
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
                        xaxis=dict(showgrid=True, gridcolor="#2a323e"),
                        yaxis=dict(showgrid=True, gridcolor="#2a323e"),
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(
                        "선택한 기간의 차트 데이터를 불러올 수 없습니다."
                    )
            except Exception:
                st.error("차트를 불러오는 중 오류가 발생했습니다.")


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

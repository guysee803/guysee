import pandas as pd
import streamlit as st
import yfinance as yf

# 웹페이지 기본 설정
st.set_page_config(
    page_title="나만의 맞춤형 주식 대시보드", page_icon="📈", layout="wide"
)

st.title("📈 내 주식 포트폴리오 실시간 대시보드")
st.markdown("매일 자동으로 업데이트되는 보유 종목 시세와 평가 손익을 확인하세요.")

# 보유 종목 리스트 (종목명, 티커, 수량, 매수가, 통화)
portfolio_data = [
    {
        "category": "해외주식",
        "name": "크리에이트 엔터프라이즈",
        "ticker": "CRE8",
        "shares": 15,
        "avg_price": 4.48,
        "currency": "USD",
    },
    {
        "category": "국내주식",
        "name": "SK스퀘어",
        "ticker": "402340.KS",
        "shares": 2,
        "avg_price": 1990000,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "SK하이닉스",
        "ticker": "000660.KS",
        "shares": 2,
        "avg_price": 2545000,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "두산에너빌리티",
        "ticker": "034020.KS",
        "shares": 10,
        "avg_price": 82950,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "우리금융지주",
        "ticker": "316140.KS",
        "shares": 10,
        "avg_price": 32015,
        "currency": "KRW",
    },
    {
        "category": "해외주식",
        "name": "NVDL",
        "ticker": "NVDL",
        "shares": 4.23,
        "avg_price": 29.06,
        "currency": "USD",
    },
    {
        "category": "국내주식",
        "name": "TIGER 200",
        "ticker": "102110.KS",
        "shares": 1,
        "avg_price": 100995,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "KODEX 200",
        "ticker": "069500.KS",
        "shares": 1,
        "avg_price": 101155,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "KODEX 코스닥150",
        "ticker": "229200.KS",
        "shares": 1,
        "avg_price": 20100,
        "currency": "KRW",
    },
    {
        "category": "국내주식",
        "name": "삼성전자",
        "ticker": "005930.KS",
        "shares": 20,
        "avg_price": 126052,
        "currency": "KRW",
    },
    {
        "category": "해외주식",
        "name": "엔비디아 (종합계좌)",
        "ticker": "NVDA",
        "shares": 2.748,
        "avg_price": 192.28,
        "currency": "USD",
    },
    {
        "category": "국내주식(ISA)",
        "name": "TIGER 미국배당다우존스타겟커버드콜1호",
        "ticker": "476970.KS",
        "shares": 13,
        "avg_price": 13506,
        "currency": "KRW",
    },
    {
        "category": "국내주식(ISA)",
        "name": "PLUS 고배당주",
        "ticker": "294230.KS",
        "shares": 5,
        "avg_price": 26627,
        "currency": "KRW",
    },
    {
        "category": "해외주식(RIA)",
        "name": "엔비디아 (RIA계좌)",
        "ticker": "NVDA",
        "shares": 1,
        "avg_price": 182.23,
        "currency": "USD",
    },
]


# 원/달러 환율 가져오기
@st.cache_data(ttl=3600)
def get_exchange_rate():
    try:
        ticker = yf.Ticker("USDCKR=X")
        return ticker.history(period="1d")["Close"].iloc[-1]
    except:
        return 1350.0


usd_krw = get_exchange_rate()


# 실시간 시세 및 손익 계산 함수
def fetch_stock_data(item):
    try:
        stock = yf.Ticker(item["ticker"])
        hist = stock.history(period="1d")
        current_price = hist["Close"].iloc[-1] if not hist.empty else item["avg_price"]
    except:
        current_price = item["avg_price"]

    if item["currency"] == "USD":
        current_val_krw = current_price * item["shares"] * usd_krw
        profit_krw = current_val_krw - (item["avg_price"] * item["shares"] * usd_krw)
        profit_rate = ((current_price - item["avg_price"]) / item["avg_price"]) * 100
    else:
        current_val_krw = current_price * item["shares"]
        profit_krw = current_val_krw - (item["avg_price"] * item["shares"])
        profit_rate = ((current_price - item["avg_price"]) / item["avg_price"]) * 100

    return {
        "구분": item["category"],
        "종목명": item["name"],
        "보유수량": item["shares"],
        "평균매수가": item["avg_price"],
        "현재가": current_price,
        "통화": item["currency"],
        "평가금액(원)": current_val_krw,
        "평가손익(원)": profit_krw,
        "수익률(%)": profit_rate,
    }


with st.spinner("실시간 주가 정보를 불러오는 중입니다..."):
    processed_data = [fetch_stock_data(item) for item in portfolio_data]

df = pd.DataFrame(processed_data)

# 요약 데이터 계산
total_current_value = df["평가금액(원)"].sum()
total_invest_value = (df["평가금액(원)"] - df["평가손익(원)"]).sum()
total_profit = df["평가손익(원)"].sum()
total_profit_rate = (
    (total_profit / total_invest_value) * 100 if total_invest_value > 0 else 0
)

# 화면 상단 요약 지표
col1, col2, col3 = st.columns(3)
col1.metric("총 평가금액", f"{total_current_value:,.0f} 원")
col2.metric("총 투자원금", f"{total_invest_value:,.0f} 원")
col3.metric(
    "총 평가손익", f"{total_profit:,.0f} 원", delta=f"{total_profit_rate:.2f}%"
)

st.markdown("---")
st.subheader("📋 보유 종목 상세 현황")

# 보기 편하게 꾸미기
display_df = df.copy()
display_df["평가금액(원)"] = display_df["평가금액(원)"].apply(lambda x: f"{x:,.0f} 원")
display_df["평가손익(원)"] = display_df["평가손익(원)"].apply(lambda x: f"{x:,.0f} 원")
display_df["수익률(%)"] = display_df["수익률(%)"].apply(lambda x: f"{x:.2f}%")

st.dataframe(display_df, use_container_width=True)

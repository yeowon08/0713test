import streamlit as st
import pandas as pd

st.set_page_config(page_title="도시 열섬현상 분석", layout="wide")

st.title("🌆 서울-양평 도시 열섬현상 분석")
st.write("서울과 양평의 시간별 기온 데이터를 비교하여 도시 열섬현상을 살펴봅니다.")

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

    return seoul, yangpyeong

seoul, yangpyeong = load_data()

# -----------------------------
# 데이터 전처리
# -----------------------------
seoul = seoul[["일시", "기온(°C)"]].rename(
    columns={"기온(°C)": "서울"}
)

yangpyeong = yangpyeong[["일시", "기온(°C)"]].rename(
    columns={"기온(°C)": "양평"}
)

merged = pd.merge(seoul, yangpyeong, on="일시")

merged["기온차"] = merged["서울"] - merged["양평"]
merged["시"] = merged["일시"].dt.hour
merged["월"] = merged["일시"].dt.month

# -----------------------------
# 1. 연간 기온 변화
# -----------------------------
st.header("① 1년간 두 지역의 기온 변화")

year_temp = merged[["일시", "서울", "양평"]].set_index("일시")

st.line_chart(year_temp)

# -----------------------------
# 2. 시각별 평균 기온차
# -----------------------------
st.header("② 시각(0~23시)별 평균 기온차")
st.caption("기온차 = 서울 − 양평")

hour_diff = (
    merged.groupby("시")["기온차"]
    .mean()
    .reset_index()
    .set_index("시")
)

st.bar_chart(hour_diff)

st.dataframe(
    hour_diff.round(2),
    use_container_width=True
)

# -----------------------------
# 3. 월별 평균 기온차
# -----------------------------
st.header("③ 월(1~12월)별 평균 기온차")
st.caption("기온차 = 서울 − 양평")

month_diff = (
    merged.groupby("월")["기온차"]
    .mean()
    .reset_index()
    .set_index("월")
)

st.bar_chart(month_diff)

st.dataframe(
    month_diff.round(2),
    use_container_width=True
)

# -----------------------------
# 요약 통계
# -----------------------------
st.header("📊 분석 결과 요약")

avg_diff = merged["기온차"].mean()

st.metric(
    "연평균 기온차 (서울 - 양평)",
    f"{avg_diff:.2f} °C"
)

if avg_diff > 0:
    st.success(
        "서울이 양평보다 평균적으로 더 따뜻하게 나타나 도시 열섬현상의 경향을 확인할 수 있습니다."
    )
else:
    st.warning(
        "서울이 양평보다 반드시 더 따뜻하다고 보기 어려운 결과입니다."
    )

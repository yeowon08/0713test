import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="도시 열섬현상과 전력수요 분석",
    layout="wide"
)

st.title("🌆 도시 열섬현상과 전력수요 분석")
st.write(
    "서울·양평 기온 데이터를 이용해 도시 열섬현상을 분석하고, "
    "서울 기온과 전력수요의 관계를 살펴봅니다."
)

# ==================================================
# 데이터 불러오기
# ==================================================
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])
    power["일시"] = pd.to_datetime(power["일시"])

    return seoul, yangpyeong, power


seoul, yangpyeong, power = load_data()

# ==================================================
# 데이터 전처리
# ==================================================
seoul_temp = seoul[["일시", "기온(°C)"]].rename(
    columns={"기온(°C)": "서울기온"}
)

yang_temp = yangpyeong[["일시", "기온(°C)"]].rename(
    columns={"기온(°C)": "양평기온"}
)

# 열섬 분석용
heat_df = pd.merge(
    seoul_temp,
    yang_temp,
    on="일시"
)

heat_df["기온차"] = (
    heat_df["서울기온"] - heat_df["양평기온"]
)

heat_df["시"] = heat_df["일시"].dt.hour
heat_df["월"] = heat_df["일시"].dt.month

# 전력 분석용
power_df = pd.merge(
    seoul_temp,
    power,
    on="일시"
)

power_df["월"] = power_df["일시"].dt.month

# 기온 구간 생성
power_df["기온구간"] = pd.cut(
    power_df["서울기온"],
    bins=[-30, -20, -10, 0, 10, 20, 30, 40, 50],
    labels=[
        "-20~-10",
        "-10~0",
        "0~10",
        "10~20",
        "20~30",
        "30~40",
        "40~50",
        "50 이상"
    ]
)

# ==================================================
# 탭 구성
# ==================================================
tab1, tab2 = st.tabs(
    ["🌆 열섬 분석", "⚡ 전력 연결"]
)

# ==================================================
# 탭1 : 열섬 분석
# ==================================================
with tab1:

    st.header("서울·양평 도시 열섬현상 분석")

    # ① 연간 기온 변화
    st.subheader("① 1년간 두 지역 기온 변화")

    yearly_temp = heat_df[
        ["일시", "서울기온", "양평기온"]
    ].set_index("일시")

    st.line_chart(yearly_temp)

    # ② 시각별 평균 기온차
    st.subheader("② 시각별 평균 기온차 (서울 - 양평)")

    hour_diff = (
        heat_df.groupby("시")["기온차"]
        .mean()
        .to_frame()
    )

    st.bar_chart(hour_diff)

    # ③ 월별 평균 기온차
    st.subheader("③ 월별 평균 기온차 (서울 - 양평)")

    month_diff = (
        heat_df.groupby("월")["기온차"]
        .mean()
        .to_frame()
    )

    st.bar_chart(month_diff)

    st.metric(
        "연평균 기온차",
        f"{heat_df['기온차'].mean():.2f} °C"
    )

# ==================================================
# 탭2 : 전력 연결
# ==================================================
with tab2:

    st.header("서울 기온과 전력수요의 관계")

    # ① 산점도
    st.subheader("① 기온과 전력수요 산점도")

    scatter_data = power_df.rename(
        columns={
            "서울기온": "기온(°C)",
            "전력수요(MWh)": "전력수요(MWh)"
        }
    )

    st.scatter_chart(
        scatter_data,
        x="기온(°C)",
        y="전력수요(MWh)"
    )

    # ② 기온 구간별 평균 전력수요
    st.subheader("② 기온 구간별 평균 전력수요")

    temp_power = (
        power_df.groupby("기온구간")["전력수요(MWh)"]
        .mean()
        .to_frame()
    )

    st.bar_chart(temp_power)

    # ③ 월별 평균 전력수요
    st.subheader("③ 월별 평균 전력수요")

    month_power = (
        power_df.groupby("월")["전력수요(MWh)"]
        .mean()
        .to_frame()
    )

    st.bar_chart(month_power)

    st.metric(
        "평균 전력수요",
        f"{power_df['전력수요(MWh)'].mean():,.0f} MWh"
    )

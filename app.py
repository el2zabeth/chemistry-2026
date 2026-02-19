import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import os

# -----------------------------
# 🔄 10초 자동 새로고침
# -----------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(layout="wide")
st.title("🎓 AP화학 수업 시작 설문 대시보드")

csv_url = st.text_input("📎 Google Sheets CSV 링크 입력")

# -----------------------------
# 질문 고정 설정
# -----------------------------
PIE_QUESTIONS = [
    "선행학습 관련",
    "원하는 수업 수준"
]

WORDCLOUD_QUESTIONS = [
    "AP화학 수업을 대하는 나의 마음가짐",
    "선생님께 바라는 점"
]

# -----------------------------
# 한글 폰트 설정 (Streamlit Cloud 대응)
# -----------------------------
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

# -----------------------------
# 데이터 불러오기
# -----------------------------
if csv_url:

    try:
        df = pd.read_csv(csv_url)
    except:
        st.error("CSV 링크를 확인해주세요.")
        st.stop()

    # 타임스탬프 제거
    df = df.loc[:, ~df.columns.str.contains("타임")]

    st.success(f"현재 응답 수: {len(df)} 명")

    # =============================
    # 📊 객관식 원그래프 (가로 2개)
    # =============================
    st.markdown("## 📊 객관식 응답")

    col1, col2 = st.columns(2)

    for i, question in enumerate(PIE_QUESTIONS):

        if question in df.columns:

            counts = df[question].dropna().value_counts()

            if len(counts) == 0:
                continue

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=counts.index,
                        values=counts.values,
                        hole=0.5,
                        textinfo="percent",
                        textfont_size=34
                    )
                ]
            )

            fig.update_layout(
                legend=dict(
                    font=dict(size=22)
                ),
                title=dict(
                    text=question,
                    font=dict(size=26)
                )
            )

            if i == 0:
                col1.plotly_chart(fig, use_container_width=True)
            else:
                col2.plotly_chart(fig, use_container_width=True)

    # =============================
    # 💬 서술형 워드클라우드
    # =============================
    st.markdown("## 💬 서술형 응답")

    for question in WORDCLOUD_QUESTIONS:

        if question in df.columns:

            st.subheader(question)

            responses = df[question].dropna().astype(str)

            # 텍스트 합치기
            text = " ".join(responses).strip()

            # 🔥 응답 부족 시 안전 처리
            if len(text) < 5:
                st.info("응답이 아직 충분하지 않습니다.")
                continue

            try:
                wordcloud = WordCloud(
                    font_path=font_path,
                    width=1400,
                    height=600,
                    background_color="white",
                    colormap="viridis",
                    max_words=200,
                    min_font_size=12
                ).generate(text)

                fig_wc, ax = plt.subplots(figsize=(14,6))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")

                st.pyplot(fig_wc)

            except Exception as e:
                st.error("워드클라우드 생성 중 오류 발생")
                st.write(e)

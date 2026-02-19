import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import qrcode
from io import BytesIO

# -----------------------------
# 자동 새로고침
# -----------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(layout="wide")
st.title("🎓 AP화학 수업 시작 설문 대시보드")

csv_url = st.text_input("📎 Google Sheets CSV 링크 입력")
form_url = st.text_input("📱 학생 참여용 Google Form 링크 (QR 생성용)")

# -----------------------------
# QR 코드 생성
# -----------------------------
if form_url:
    qr = qrcode.make(form_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=200)
    st.markdown("### 📌 위 QR을 학생들에게 보여주세요")

# -----------------------------
# 질문 설정
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
# 데이터 로드
# -----------------------------
if csv_url:

    try:
        df = pd.read_csv(csv_url)
    except:
        st.error("CSV 링크를 확인해주세요.")
        st.stop()

    df = df.loc[:, ~df.columns.str.contains("타임")]

    st.success(f"현재 응답 수: {len(df)} 명")

    # ============================
    # 객관식 원그래프
    # ============================
    st.markdown("## 📊 객관식 응답")

    col1, col2 = st.columns(2)

    for i, question in enumerate(PIE_QUESTIONS):

        if question in df.columns:

            counts = df[question].dropna().value_counts()

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=counts.index,
                        values=counts.values,
                        hole=0.5,
                        textinfo="percent",
                        textfont_size=36
                    )
                ]
            )

            fig.update_layout(
                legend=dict(font=dict(size=22)),
                title=dict(text=question, font=dict(size=26))
            )

            if i == 0:
                col1.plotly_chart(fig, use_container_width=True)
            else:
                col2.plotly_chart(fig, use_container_width=True)

    # ============================
    # 서술형 워드클라우드
    # ============================
    st.markdown("## 💬 서술형 응답")

    for question in WORDCLOUD_QUESTIONS:

        if question in df.columns:

            st.subheader(question)

            responses = df[question].dropna().astype(str)

            text = " ".join(responses).strip()

            if len(text) < 3:
                st.info("응답이 아직 없습니다.")
                continue

            # 🔥 폰트 예외처리 포함
            try:
                wordcloud = WordCloud(
                    font_path="NanumGothic.ttf",  # 프로젝트에 넣으면 사용
                    width=1400,
                    height=600,
                    background_color="white",
                    colormap="viridis"
                ).generate(text)

            except:
                # 폰트 없으면 기본 폰트 사용 (한글 깨질 수 있음)
                wordcloud = WordCloud(
                    width=1400,
                    height=600,
                    background_color="white",
                    colormap="viridis"
                ).generate(text)

            fig_wc, ax = plt.subplots(figsize=(14,6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig_wc)

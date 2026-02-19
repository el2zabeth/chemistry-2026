import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import qrcode
from io import BytesIO
import os

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(layout="wide")
st.title("🎓 AP화학 수업 시작 설문 대시보드")

# 자동 새로고침 (10초)
st_autorefresh(interval=10000, key="refresh")

# -----------------------------
# 입력 영역
# -----------------------------
csv_url = st.text_input("📎 Google Sheets CSV 링크 입력")
form_url = st.text_input("📱 학생 참여용 Google Form 링크 (QR 생성용)")

# -----------------------------
# QR 코드 생성
# -----------------------------
if form_url:
    qr = qrcode.make(form_url)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=220)
    st.markdown("### 📌 학생들에게 위 QR코드를 보여주세요")

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
# 폰트 경로 자동 인식
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "NanumGothic.ttf")

# -----------------------------
# 데이터 로드
# -----------------------------
if csv_url:

    try:
        df = pd.read_csv(csv_url)
    except:
        st.error("❌ CSV 링크를 다시 확인해주세요.")
        st.stop()

    # 타임스탬프 제거
    df = df.loc[:, ~df.columns.str.contains("타임|Timestamp")]

    st.success(f"현재 응답 수: {len(df)} 명")

    # ============================
    # 📊 객관식 원그래프
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
                        hole=0.45,
                        textinfo="percent+label",
                        textfont_size=30
                    )
                ]
            )

            fig.update_layout(
                title=dict(text=question, font=dict(size=26)),
                legend=dict(font=dict(size=20))
            )

            if i == 0:
                col1.plotly_chart(fig, use_container_width=True)
            else:
                col2.plotly_chart(fig, use_container_width=True)

        else:
            if i == 0:
                col1.warning(f"'{question}' 열을 찾을 수 없습니다.")
            else:
                col2.warning(f"'{question}' 열을 찾을 수 없습니다.")

    # ============================
    # 💬 서술형 워드클라우드
    # ============================
    st.markdown("## 💬 서술형 응답")

    if not os.path.exists(FONT_PATH):
        st.error("❌ NanumGothic.ttf 파일이 프로젝트에 없습니다.")
        st.stop()

    for question in WORDCLOUD_QUESTIONS:

        if question in df.columns:

            st.subheader(question)

            responses = df[question].dropna().astype(str)

            text = " ".join(responses).strip()

            if len(text) < 3:
                st.info("아직 응답이 없습니다.")
                continue

            wordcloud = WordCloud(
                font_path=FONT_PATH,
                width=1600,
                height=700,
                background_color="white",
                colormap="viridis",
                max_words=200,
                min_font_size=15
            ).generate(text)

            fig_wc, ax = plt.subplots(figsize=(16,7))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig_wc)

        else:
            st.warning(f"'{question}' 열을 찾을 수 없습니다.")


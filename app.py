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
# 자동 새로고침 (10초)
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

    # =====================================================
    # 📊 객관식 (도넛 + 오른쪽에 크게 텍스트)
    # =====================================================
    st.markdown("## 📊 객관식 응답")

    for question in PIE_QUESTIONS:

        if question in df.columns:

            counts = df[question].dropna().value_counts()
            col1, col2 = st.columns([1,1])

            # 🔵 도넛 그래프
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=counts.index,
                        values=counts.values,
                        hole=0.6,
                        textinfo="percent",   # 퍼센트만 표시
                        textfont_size=30
                    )
                ]
            )

            fig.update_layout(
                showlegend=False,
                title=dict(text=question, font=dict(size=26))
            )

            col1.plotly_chart(fig, use_container_width=True)

            # 🔵 오른쪽 큰 텍스트 표시
            with col2:
                st.markdown(f"### 📌 {question}")
                total = counts.sum()

                for label, value in counts.items():
                    percent = round(value / total * 100, 1)
                    st.markdown(
                        f"<p style='font-size:28px'><b>{label}</b> : {percent}%</p>",
                        unsafe_allow_html=True
                    )

    # =====================================================
    # 💬 서술형 워드클라우드 (완전 안정화 버전)
    # =====================================================
    st.markdown("## 💬 서술형 응답")

    for question in WORDCLOUD_QUESTIONS:

        if question in df.columns:

            st.subheader(question)

            responses = df[question].dropna().astype(str)

            text = " ".join(responses).strip()

            if len(text) < 5:
                st.info("응답이 아직 없습니다.")
                continue

            # 🔥 폰트 경로 자동 탐색
            font_path = None

            possible_paths = [
                "NanumGothic.ttf",
                "./NanumGothic.ttf",
                "fonts/NanumGothic.ttf"
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    font_path = path
                    break

            try:
                if font_path:
                    wordcloud = WordCloud(
                        font_path=font_path,
                        width=1400,
                        height=600,
                        background_color="white",
                        colormap="viridis"
                    ).generate(text)
                else:
                    st.warning("⚠️ 나눔고딕 폰트를 찾지 못했습니다.")
                    st.stop()

            except Exception as e:
                st.error("워드클라우드 생성 오류")
                st.text(e)
                st.stop()

            fig_wc, ax = plt.subplots(figsize=(14,6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig_wc)

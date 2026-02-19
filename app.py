import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import random
import string
import os
import qrcode
from io import BytesIO

# ---------------------------
# 자동 새로고침 (10초)
# ---------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="수업 시작 설문", layout="wide")

st.title("AP 화학")

# ---------------------------
# 참여코드 생성
# ---------------------------
if "class_code" not in st.session_state:
    st.session_state.class_code = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

st.markdown(f"## 🎟 참여 코드: `{st.session_state.class_code}`")

# ---------------------------
# QR 코드 생성
# ---------------------------
form_link = st.text_input("📎 Google Form 링크 (QR 생성용)")

if form_link:
    qr = qrcode.make(form_link)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), width=220)

st.markdown("---")

csv_url = st.text_input("📎 Google Sheets CSV 링크 입력")

# ---------------------------
# 한글 폰트
# ---------------------------
def get_korean_font():
    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None

font_path = get_korean_font()

if csv_url:
    try:
        df = pd.read_csv(csv_url)

        # 타임스탬프 제거
        df = df.loc[:, ~df.columns.str.contains("타임")]

        # 참여코드 필터
        if "코드" in df.columns:
            df = df[df["코드"] == st.session_state.class_code]

        st.success(f"현재 응답 수: {len(df)} 명")

        columns = df.columns.tolist()

        # 객관식/서술형 자동 분류
        objective_cols = []
        subjective_cols = []

        for col in columns:
            if df[col].nunique() <= 10:
                objective_cols.append(col)
            else:
                subjective_cols.append(col)

        # =========================
        # 📊 객관식 2개 가로배치
        # =========================
        st.markdown("## 📊 객관식 응답")

        col1, col2 = st.columns(2)

        for i in range(min(2, len(objective_cols))):
            col_name = objective_cols[i]
            counts = df[col_name].value_counts()

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=counts.index,
                        values=counts.values,
                        hole=0.5,
                        textinfo="percent",   # 퍼센트만
                        textfont_size=28
                    )
                ]
            )

            fig.update_layout(
                showlegend=True,
                legend=dict(
                    font=dict(size=20)  # 범례 크게
                ),
                title=dict(
                    text=col_name,
                    font=dict(size=26)
                )
            )

            if i == 0:
                col1.plotly_chart(fig, use_container_width=True)
            else:
                col2.plotly_chart(fig, use_container_width=True)

        # =========================
        # 💬 서술형 응답 2개
        # =========================
        st.markdown("## 💬 서술형 응답")

        for col in subjective_cols[:2]:
            st.subheader(col)

            responses = df[col].dropna().astype(str)

            if len(responses) > 0:

                # 🔥 모든 텍스트를 하나로 합쳐 워드클라우드 생성
                text = " ".join(responses)

                wordcloud = WordCloud(
                    font_path=font_path,
                    width=1400,
                    height=600,
                    background_color="white",
                    colormap="viridis",
                    max_words=150
                ).generate(text)

                fig_wc, ax = plt.subplots(figsize=(14,6))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")

                st.pyplot(fig_wc)

            else:
                st.info("아직 응답이 없습니다.")

    except Exception as e:
        st.error("CSV 오류 또는 공유 설정 문제")
        st.text(str(e))

else:
    st.info("CSV 링크를 입력하면 자동으로 표시됩니다.")

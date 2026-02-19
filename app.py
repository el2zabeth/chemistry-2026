import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import random
import string
import os
import qrcode
from io import BytesIO

# ---------------------------
# 🔄 10초 자동 새로고침
# ---------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="우리 반 수업 설문", layout="wide")

st.title("🎓 우리 반 수업 시작 설문")

# ---------------------------
# 🎟 참여코드 생성
# ---------------------------
if "class_code" not in st.session_state:
    st.session_state.class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

st.markdown(f"## 🎟 참여 코드: `{st.session_state.class_code}`")

# ---------------------------
# QR 코드 생성
# ---------------------------
form_link = st.text_input("📎 학생들에게 제공할 Google Form 링크 입력 (QR 생성용)")

if form_link:
    qr = qrcode.make(form_link)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="📱 QR코드를 스캔하여 참여하세요", width=200)

st.markdown("---")

csv_url = st.text_input("📎 Google Sheets CSV URL 입력")

# ---------------------------
# 한글 폰트 설정
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

        # 참여코드 필터링
        if "코드" in df.columns:
            df = df[df["코드"] == st.session_state.class_code]

        st.success(f"현재 응답 수: {len(df)} 명")

        # 반별 저장 기능
        save_folder = "saved_results"
        os.makedirs(save_folder, exist_ok=True)
        save_path = f"{save_folder}/{st.session_state.class_code}.csv"
        df.to_csv(save_path, index=False)

        columns = [c for c in df.columns if c != "코드"]

        # -----------------------------
        # 질문 분류
        # -----------------------------
        objective_cols = []
        subjective_cols = []

        for col in columns:
            if df[col].nunique() <= 10:
                objective_cols.append(col)
            else:
                subjective_cols.append(col)

        # ==========================
        # 📊 객관식 2개 가로 배치
        # ==========================
        st.markdown("## 📊 객관식 응답")

        colA, colB = st.columns(2)

        for i in range(min(2, len(objective_cols))):
            counts = df[objective_cols[i]].value_counts().reset_index()
            counts.columns = ["선택지", "응답 수"]

            fig = px.pie(
                counts,
                names="선택지",
                values="응답 수",
                hole=0.4
            )

            fig.update_traces(
                textfont_size=18,
                textinfo="percent+label"
            )

            fig.update_layout(
                title_font_size=22
            )

            if i == 0:
                colA.subheader(objective_cols[i])
                colA.plotly_chart(fig, use_container_width=True)
            else:
                colB.subheader(objective_cols[i])
                colB.plotly_chart(fig, use_container_width=True)

        # ==========================
        # 💬 서술형 2개 표시
        # ==========================
        st.markdown("## 💬 서술형 응답")

        for col in subjective_cols[:2]:
            st.subheader(col)

            responses = df[col].dropna()

            if len(responses) > 0:
                freq = responses.value_counts().to_dict()

                wordcloud = WordCloud(
                    font_path=font_path,
                    width=1400,
                    height=600,
                    background_color="white",
                    colormap="viridis",
                    max_words=100
                ).generate_from_frequencies(freq)

                fig_wc, ax_wc = plt.subplots(figsize=(14,6))
                ax_wc.imshow(wordcloud, interpolation="bilinear")
                ax_wc.axis("off")

                st.pyplot(fig_wc)
            else:
                st.info("아직 응답이 없습니다.")

    except Exception as e:
        st.error("CSV 오류 또는 공개 설정 문제")
        st.text(str(e))

else:
    st.info("CSV 링크를 입력하면 실시간으로 4개 질문이 모두 표시됩니다.")

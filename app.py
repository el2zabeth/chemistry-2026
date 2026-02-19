import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import random
import string
import os

# ---------------------------
# 🔄 자동 새로고침
# ---------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="우리 반 수업 설문", layout="wide")

# ---------------------------
# 🎨 다크 테마
# ---------------------------
st.markdown("""
<style>
body { background-color: #0e1117; }
h1, h2, h3 { color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🎓 우리 반 수업 시작 설문")

# ---------------------------
# 🎟 참여코드 생성
# ---------------------------
if "class_code" not in st.session_state:
    st.session_state.class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

st.markdown(f"""
### 🎟 학생 참여 코드  
## `{st.session_state.class_code}`
학생들은 설문에서 이 코드를 입력하세요.
""")

st.markdown("---")

csv_url = st.text_input("📎 Google Sheets CSV URL 입력")

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

        # 참여코드 필터링 (설문에 '코드'라는 질문이 있다고 가정)
        if "코드" in df.columns:
            df = df[df["코드"] == st.session_state.class_code]

        st.success(f"현재 응답 수: {len(df)} 명")

        columns = df.columns.tolist()

        # -----------------------------
        # 질문 자동 분류
        # -----------------------------
        objective_cols = []
        subjective_cols = []

        for col in columns:
            if col == "코드":
                continue
            if df[col].nunique() <= 10:
                objective_cols.append(col)
            else:
                subjective_cols.append(col)

        # ==========================
        # 📊 객관식 2개 가로 배치
        # ==========================
        st.markdown("## 📊 객관식 응답")

        if len(objective_cols) >= 2:
            col1, col2 = st.columns(2)

            for i in range(2):
                counts = df[objective_cols[i]].value_counts().reset_index()
                counts.columns = ["선택지", "응답 수"]

                fig = px.pie(
                    counts,
                    names="선택지",
                    values="응답 수",
                    hole=0.5
                )

                fig.update_layout(
                    paper_bgcolor="#0e1117",
                    font=dict(color="white"),
                    transition_duration=800
                )

                if i == 0:
                    col1.subheader(objective_cols[i])
                    col1.plotly_chart(fig, use_container_width=True)
                else:
                    col2.subheader(objective_cols[i])
                    col2.plotly_chart(fig, use_container_width=True)

        # ==========================
        # 💬 서술형 2개 표시
        # ==========================
        st.markdown("## 💬 서술형 응답")

        for col in subjective_cols[:2]:
            st.subheader(col)

            freq = df[col].dropna().value_counts().to_dict()

            wordcloud = WordCloud(
                font_path=font_path,
                width=1400,
                height=600,
                background_color="#0e1117",
                colormap="viridis"
            ).generate_from_frequencies(freq)

            fig_wc, ax_wc = plt.subplots(figsize=(14,6))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")

            st.pyplot(fig_wc)

    except Exception as e:
        st.error("CSV 오류 또는 공개 설정 문제")
        st.text(str(e))

else:
    st.info("CSV 링크를 입력하면 실시간으로 4개 질문이 모두 표시됩니다.")


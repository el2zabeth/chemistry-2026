import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import matplotlib.font_manager as fm
import os

# ---------------------------
# 🔄 10초 자동 새로고침
# ---------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(
    page_title="수업 시작 설문 대시보드",
    layout="wide",
)

# ---------------------------
# 🎨 다크 스타일 적용
# ---------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 우리 반 수업 시작 설문")

st.markdown("Google Sheets → 웹에 게시 → CSV 링크 입력")

csv_url = st.text_input("📎 CSV URL 입력")

# ---------------------------
# 한글 폰트 설정 (Streamlit Cloud용 안전 설정)
# ---------------------------
def get_korean_font():
    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return path
    return None

font_path = get_korean_font()

if csv_url:

    try:
        df = pd.read_csv(csv_url)
        st.success("✅ 실시간 연결 완료")
        st.write(f"현재 응답 수: {len(df)} 명")

        columns = df.columns.tolist()

        st.markdown("---")

        question = st.selectbox("📌 질문 선택", columns)

        if question:

            responses = df[question].dropna()

            # -----------------------------
            # 객관식 여부 판단 (고유값 10개 이하 → 객관식으로 간주)
            # -----------------------------
            if responses.nunique() <= 10:

                st.subheader("📊 응답 비율 (도넛 차트)")

                counts = responses.value_counts().reset_index()
                counts.columns = ["선택지", "응답 수"]

                fig = px.pie(
                    counts,
                    names="선택지",
                    values="응답 수",
                    hole=0.5,
                )

                fig.update_traces(textinfo='percent+label')
                fig.update_layout(
                    paper_bgcolor="#0e1117",
                    font=dict(color="white"),
                    transition_duration=800
                )

                st.plotly_chart(fig, use_container_width=True)

            # -----------------------------
            # 서술형 → Mentimeter 스타일
            # -----------------------------
            else:

                st.subheader("💬 우리 반 생각 보기")

                freq = responses.value_counts().to_dict()

                wordcloud = WordCloud(
                    font_path=font_path,
                    width=1400,
                    height=700,
                    background_color="#0e1117",
                    colormap="viridis",
                    prefer_horizontal=1.0,
                    max_words=100
                ).generate_from_frequencies(freq)

                fig_wc, ax_wc = plt.subplots(figsize=(16,8))
                ax_wc.imshow(wordcloud, interpolation="bilinear")
                ax_wc.axis("off")

                st.pyplot(fig_wc)

    except Exception as e:
        st.error("❌ CSV 링크 오류 또는 공개 설정 문제")
        st.text(str(e))

else:
    st.info("CSV 링크를 입력하면 10초마다 자동 업데이트됩니다.")

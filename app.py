import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from streamlit_autorefresh import st_autorefresh
import os

st_autorefresh(interval=10000, key="refresh")

st.set_page_config(layout="wide")
st.title("🎓 수업 시작 설문 대시보드")

csv_url = st.text_input("📎 Google Sheets CSV 링크 입력")

# -----------------------------
# 한글 폰트 설정
# -----------------------------
font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

if csv_url:
    df = pd.read_csv(csv_url)

    # 타임스탬프 제거
    df = df.loc[:, ~df.columns.str.contains("타임")]

    # 코드 컬럼 제거
    df = df.loc[:, ~df.columns.str.contains("코드")]

    st.success(f"현재 응답 수: {len(df)} 명")

    columns = df.columns.tolist()

    objective_cols = []
    subjective_cols = []

    # 🔥 새 분류 방식
    for col in columns:
        sample_text = df[col].dropna().astype(str)

        if len(sample_text) == 0:
            continue

        avg_length = sample_text.str.len().mean()

        # 평균 글자수 기준
        if avg_length < 15:
            objective_cols.append(col)
        else:
            subjective_cols.append(col)

    # ============================
    # 📊 객관식 (최대 2개 가로배치)
    # ============================
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
                    textinfo="percent",
                    textfont_size=28
                )
            ]
        )

        fig.update_layout(
            legend=dict(font=dict(size=20)),
            title=dict(text=col_name, font=dict(size=26))
        )

        if i == 0:
            col1.plotly_chart(fig, use_container_width=True)
        else:
            col2.plotly_chart(fig, use_container_width=True)

    # ============================
    # 💬 서술형 워드클라우드
    # ============================
    st.markdown("## 💬 서술형 응답")

    for col in subjective_cols[:2]:
        st.subheader(col)

        responses = df[col].dropna().astype(str)

        if len(responses) > 0:
            text = " ".join(responses)

            wordcloud = WordCloud(
                font_path=font_path,
                width=1400,
                height=600,
                background_color="white",
                colormap="viridis",
                max_words=200,
                min_font_size=10
            ).generate(text)

            fig_wc, ax = plt.subplots(figsize=(14,6))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig_wc)

        else:
            st.info("응답이 아직 없습니다.")

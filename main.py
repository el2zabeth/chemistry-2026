streamlit
pandas
plotly
wordcloud
numpy

import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter
import numpy as np

st.set_page_config(page_title="설문 대시보드 PRO", layout="wide")

st.title("📊 Google Form 설문 결과 대시보드 PRO")
st.markdown("Plotly 기반 인터랙티브 분석 + 멘티미터 스타일")

# 🔗 Google Sheets CSV 링크 입력
sheet_url = st.text_input("Google Sheets CSV 링크 입력")

if sheet_url:

    try:
        df = pd.read_csv(sheet_url)
        st.success("데이터 불러오기 성공!")

        # 📌 응답 수 표시
        st.metric("총 응답 수", len(df))

        # 질문 선택
        question = st.selectbox("분석할 질문 선택", df.columns)

        if question:

            st.subheader(f"📊 '{question}' 분석 결과")

            # 객관식 처리
            if df[question].nunique() < 20:

                value_counts = df[question].value_counts().reset_index()
                value_counts.columns = ["응답", "빈도"]

                chart_type = st.radio("그래프 유형 선택", ["막대그래프", "파이차트"])

                if chart_type == "막대그래프":
                    fig = px.bar(
                        value_counts,
                        x="응답",
                        y="빈도",
                        color="응답",
                        text="빈도",
                        template="plotly_dark"
                    )
                else:
                    fig = px.pie(
                        value_counts,
                        names="응답",
                        values="빈도",
                        template="plotly_dark"
                    )

                st.plotly_chart(fig, use_container_width=True)

            # 주관식 처리 (멘티미터 스타일)
            else:

                text = " ".join(str(x) for x in df[question].dropna())

                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color="black",
                    colormap=np.random.choice(
                        ["viridis", "plasma", "inferno", "magma", "cool"]
                    ),
                ).generate(text)

                st.subheader("☁️ 워드클라우드")

                st.image(wordcloud.to_array())

                # 🔥 TOP 10 키워드
                words = text.split()
                word_counts = Counter(words).most_common(10)

                top_df = pd.DataFrame(word_counts, columns=["단어", "빈도"])

                fig2 = px.bar(
                    top_df,
                    x="단어",
                    y="빈도",
                    color="단어",
                    template="plotly_dark",
                    text="빈도"
                )

                st.subheader("🔥 TOP 10 키워드")
                st.plotly_chart(fig2, use_container_width=True)

        # 📈 시간대 분석 (Timestamp 있을 경우)
        if "Timestamp" in df.columns:

            st.subheader("📈 시간대별 응답 추이")

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            time_count = df.groupby(df["Timestamp"].dt.date).size().reset_index()
            time_count.columns = ["날짜", "응답수"]

            fig3 = px.line(
                time_count,
                x="날짜",
                y="응답수",
                markers=True,
                template="plotly_dark"
            )

            st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error("데이터를 불러오지 못했습니다. CSV 링크를 확인하세요.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import numpy as np
import time

st.set_page_config(page_title="설문 결과 대시보드 PRO", layout="wide")

st.title("📊 Google Form 설문 결과 대시보드 PRO")
st.markdown("실시간 설문 응답 분석 + 멘티미터 스타일 시각화")

# 자동 새로고침 옵션
auto_refresh = st.checkbox("🔄 30초마다 자동 새로고침")

if auto_refresh:
    st.experimental_rerun()

sheet_url = st.text_input("Google Sheets CSV 링크 입력")

if sheet_url:
    try:
        df = pd.read_csv(sheet_url)
        st.success("데이터 불러오기 성공!")

        # 응답 수 표시
        st.metric("📌 총 응답 수", len(df))

        # 질문 선택
        question = st.selectbox("분석할 질문 선택", df.columns)

        if question:

            st.subheader(f"📊 '{question}' 분석")

            col1, col2 = st.columns(2)

            # 객관식 처리
            if df[question].nunique() < 20:

                chart_type = st.radio("그래프 유형 선택", ["막대그래프", "파이차트"])

                value_counts = df[question].value_counts()

                fig, ax = plt.subplots()

                if chart_type == "막대그래프":
                    value_counts.plot(kind='bar', ax=ax, color="skyblue")
                else:
                    value_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)

                plt.xticks(rotation=45)
                st.pyplot(fig)

            # 주관식 처리
            else:

                text = " ".join(str(x) for x in df[question].dropna())

                # 워드클라우드
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    colormap=np.random.choice(["viridis", "plasma", "inferno", "cool"])
                ).generate(text)

                st.subheader("☁️ 멘티미터 스타일 워드클라우드")

                fig, ax = plt.subplots(figsize=(10,5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)

                # 🔥 상위 키워드 TOP 10
                words = text.split()
                word_counts = Counter(words).most_common(10)

                st.subheader("🔥 TOP 10 키워드")

                top_df = pd.DataFrame(word_counts, columns=["단어", "빈도"])
                st.bar_chart(top_df.set_index("단어"))

        # ⏰ 시간대 분석 (타임스탬프 있을 경우)
        if "Timestamp" in df.columns:
            st.subheader("📈 시간대별 응답 추이")

            df["Timestamp"] = pd.to_datetime(df["Timestamp"])
            time_count = df.groupby(df["Timestamp"].dt.date).size()

            st.line_chart(time_count)

        # 📊 다중 질문 비교
        st.subheader("📊 질문 간 비교")

        multi_questions = st.multiselect("비교할 질문 선택", df.columns)

        if multi_questions:
            compare_df = df[multi_questions]
            st.dataframe(compare_df)

    except:
        st.error("데이터를 불러오지 못했습니다. 링크를 확인하세요.")

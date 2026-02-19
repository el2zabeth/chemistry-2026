import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
from wordcloud import WordCloud
import plotly.express as px
from scipy.stats import chi2_contingency
from streamlit_autorefresh import st_autorefresh

# ---------------------------
# 🔄 10초 자동 새로고침
# ---------------------------
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="Live Survey Dashboard", layout="wide")

st.title("📊 실시간 Google Form 설문 대시보드")

st.markdown("Google Sheets에서 '웹에 게시 → CSV 링크'를 입력하세요.")

# ---------------------------
# 📥 CSV URL 입력
# ---------------------------
csv_url = st.text_input("📎 Google Sheets CSV URL 입력")

if csv_url:

    try:
        df = pd.read_csv(csv_url)

        st.success("✅ 실시간 데이터 연결 성공")
        st.write(f"총 응답 수: {len(df)}")
        st.dataframe(df.head())

        columns = df.columns.tolist()

        # ================================
        # 🔵 벤다이어그램
        # ================================
        st.subheader("🔵 벤다이어그램 (2~3개 선택)")

        selected_cols = st.multiselect("질문 선택", columns)

        if len(selected_cols) == 2:
            set1 = set(df[selected_cols[0]].dropna())
            set2 = set(df[selected_cols[1]].dropna())
            fig, ax = plt.subplots()
            venn2([set1, set2], set_labels=selected_cols)
            st.pyplot(fig)

        elif len(selected_cols) == 3:
            set1 = set(df[selected_cols[0]].dropna())
            set2 = set(df[selected_cols[1]].dropna())
            set3 = set(df[selected_cols[2]].dropna())
            fig, ax = plt.subplots()
            venn3([set1, set2, set3], set_labels=selected_cols)
            st.pyplot(fig)

        # ================================
        # 📊 Mentimeter 스타일 막대그래프
        # ================================
        st.subheader("📊 실시간 투표 결과")

        vote_col = st.selectbox("투표 질문 선택", columns)

        if vote_col:
            vote_counts = df[vote_col].value_counts().reset_index()
            vote_counts.columns = ["Option", "Votes"]

            fig = px.bar(
                vote_counts,
                x="Option",
                y="Votes",
                title="실시간 응답 현황"
            )

            st.plotly_chart(fig, use_container_width=True)

        # ================================
        # ☁️ 워드클라우드
        # ================================
        st.subheader("☁️ 실시간 워드클라우드")

        text_col = st.selectbox("서술형 질문 선택", columns)

        if text_col:
            text_data = " ".join(df[text_col].dropna().astype(str))

            wordcloud = WordCloud(
                width=1000,
                height=400,
                background_color="white"
            ).generate(text_data)

            fig_wc, ax_wc = plt.subplots(figsize=(12,5))
            ax_wc.imshow(wordcloud, interpolation="bilinear")
            ax_wc.axis("off")

            st.pyplot(fig_wc)

        # ================================
        # 📈 카이제곱 검정
        # ================================
        st.subheader("📈 변수 관계 분석 (카이제곱 검정)")

        colA = st.selectbox("변수 A", columns, key="A")
        colB = st.selectbox("변수 B", columns, key="B")

        if colA and colB:
            contingency = pd.crosstab(df[colA], df[colB])
            chi2, p, dof, expected = chi2_contingency(contingency)

            st.write("카이제곱 통계량:", round(chi2, 3))
            st.write("p-value:", round(p, 5))

            if p < 0.05:
                st.success("통계적으로 유의미한 관계가 있습니다 (p < 0.05)")
            else:
                st.info("통계적으로 유의미하지 않습니다")

        # ================================
        # ⬇ CSV 다운로드
        # ================================
        st.subheader("⬇ 데이터 다운로드")

        csv_download = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "CSV 다운로드",
            data=csv_download,
            file_name="survey_results.csv",
            mime="text/csv"
        )

    except:
        st.error("❌ CSV 링크가 올바르지 않습니다.")

else:
    st.info("CSV 링크를 입력하면 10초마다 자동으로 업데이트됩니다.")

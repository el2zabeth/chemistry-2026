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
        st.subheader("🔵 벤다이어

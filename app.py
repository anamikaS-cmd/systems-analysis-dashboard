import pandas as pd
import plotly.express as px
import streamlit as st

# 1. НАСТРОЙКА СТРАНИЦЫ
st.set_page_config(page_title="GoT Episodes Dashboard", layout="wide")
st.title("🎬 Дашборд: Статистика и рейтинги эпизодов Игре Престолов")

# 2. ПОДГОТОВКА И ОЧИСТКА ДАННЫХ
@st.cache_data
def load_and_clean_data():
    # Пробуем стандартную кодировку, если нет - берем cp1251
    try:
        df = pd.read_csv("Game_of_Thrones.csv", encoding="utf-8")
    except:
        df = pd.read_csv("Game_of_Thrones.csv", encoding="cp1251")
    
    df = df.dropna(subset=["Title of the Episode", "Season", "IMDb Rating"])
    df["Season"] = df["Season"].astype(int)
    df["Running Time (Minutes)"] = pd.to_numeric(df["Running Time (Minutes)"], errors="coerce")
    df["IMDb Rating"] = pd.to_numeric(df["IMDb Rating"], errors="coerce")
    df["U.S. Viewers (Millions)"] = pd.to_numeric(df["U.S. Viewers (Millions)"], errors="coerce")
    df["Directed by"] = df["Directed by"].str.strip()
    df["Popularity_Score"] = round(df["IMDb Rating"] * df["U.S. Viewers (Millions)"], 2)
    return df

df = load_and_clean_data()

# 3. РЕАЛИЗАЦИЯ ФИЛЬТРОВ
st.sidebar.header("Фильтры дашборда")
all_seasons = ["Все сезоны"] + sorted(list(df["Season"].unique()))
selected_season = st.sidebar.selectbox("Главный фильтр: Сезон", all_seasons)

if selected_season != "Все сезоны":
    df_filtered = df[df["Season"] == selected_season]
else:
    df_filtered = df.copy()

all_directors = sorted(list(df_filtered["Directed by"].dropna().unique()))
selected_directors = st.sidebar.multiselect("Вторичный фильтр: Режиссеры", all_directors, default=all_directors)

if selected_directors:
    df_filtered = df_filtered[df_filtered["Directed by"].isin(selected_directors)]

# 4. KPI КАРТОЧКИ
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Всего эпизодов", value=len(df_filtered))
with col2:
    avg_rating = round(df_filtered["IMDb Rating"].mean(), 2) if not df_filtered.empty else 0
    st.metric(label="Средний рейтинг IMDb", value=avg_rating)
with col3:
    max_viewers = df_filtered["U.S. Viewers (Millions)"].max() if not df_filtered.empty else 0
    st.metric(label="Пик просмотров в США (Млн)", value=max_viewers)
with col4:
    avg_time = round(df_filtered["Running Time (Minutes)"].mean(), 1) if not df_filtered.empty else 0
    st.metric(label="Средний хронометраж (мин)", value=avg_time)

st.markdown("---")

# 5. ГРАФИКИ
row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.subheader("📈 Динамика просмотров серий в США")
    fig_line = px.line(df_filtered, x="No. of Episode (Overall)", y="U.S. Viewers (Millions)", hover_name="Title of the Episode", template="plotly_dark")
    st.plotly_chart(fig_line, use_container_width=True)

with row1_col2:
    st.subheader("📊 Распределение оценок IMDb по сезонам")
    season_ratings = df_filtered.groupby("Season")["IMDb Rating"].mean().reset_index()
    fig_bar = px.bar(season_ratings, x="Season", y="IMDb Rating", template="plotly_dark", range_y=[5, 10])
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("🏆 Топ серий по индексу популярности")
top_episodes = df_filtered[["Season", "Title of the Episode", "Directed by", "IMDb Rating", "U.S. Viewers (Millions)", "Popularity_Score"]].sort_values(by="Popularity_Score", ascending=False).head(10).reset_index(drop=True)
st.dataframe(top_episodes, use_container_width=True)
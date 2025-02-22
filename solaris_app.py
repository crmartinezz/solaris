import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Configuración de la página de Streamlit
st.set_page_config(page_title="Análisis Solar Colombia", page_icon="🌍", layout="wide")
st.title("🗺️ Visualización y Análisis Solar en Colombia")

# Cargar datos desde el archivo CSV
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_unificados.csv")
    df['Fecha'] = pd.to_datetime(df.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1))
    return df

df_all = cargar_datos()

def get_region(lat, lon):
    if lat > 8:
        return "Caribe"
    elif lat < 2:
        return "Sur"
    elif lon < -75:
        return "Pacífico"
    return "Andina"

df_all['Region'] = df_all.apply(lambda x: get_region(x['LAT'], x['LON']), axis=1)

# Menú de navegación
menu = st.sidebar.radio("📌 Selecciona una opción:", [
    "🗺 Mapa Principal", "📊 Análisis Detallado", "📅 Comparativa Histórica", "📦 Datos", "🔍 Matriz de Correlación", "🌡 Percentiles"
])

# Mapa Principal
if menu == "🗺 Mapa Principal":
    zoom_level = st.sidebar.slider("Nivel de Zoom", 4, 15, 6)
    st.subheader("🌍 Mapa de Radiación Solar en Colombia")
    fig = px.scatter_mapbox(
        df_all, lat='LAT', lon='LON', color='ALLSKY_KT',
        size=[3]*len(df_all), hover_name='LAT', zoom=zoom_level,
        color_continuous_scale='plasma', mapbox_style='open-street-map',
        center={'lat': 4.5709, 'lon': -74.2973}
    )
    fig.update_traces(marker=dict(opacity=0.45))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=700)
    st.plotly_chart(fig, use_container_width=True)

# Análisis Detallado
elif menu == "📊 Análisis Detallado":
    st.subheader("📈 Análisis de Datos Climáticos")
    region_avg = df_all.groupby('Region')['ALLSKY_SFC_SW_DWN'].mean()
    st.bar_chart(region_avg)
    df_all['Viabilidad'] = (df_all['ALLSKY_SFC_SW_DWN'] * 0.6 + df_all['ALLSKY_KT'] * 0.4)
    top3 = df_all.nlargest(3, 'Viabilidad')
    for i, (_, row) in enumerate(top3.iterrows()):
        st.metric(f"🥇 Ubicación {i+1}", f"{row['Viabilidad']:.2f} pts", f"Lat: {row['LAT']:.4f} Lon: {row['LON']:.4f}")

# Comparativa Histórica
elif menu == "📅 Comparativa Histórica":
    st.subheader("📆 Análisis Temporal")
    año = st.sidebar.selectbox("Selecciona el año", df_all["YEAR"].unique())
    df_filtrado = df_all[df_all["YEAR"] == año]
    fig = px.line(df_filtrado, x="Fecha", y="ALLSKY_SFC_SW_DWN", title=f"Tendencia Anual {año}")
    st.plotly_chart(fig)

# Datos
elif menu == "📦 Datos":
    st.subheader("📂 Datos Disponibles")
    st.dataframe(df_all)

# Matriz de Correlación
elif menu == "🔍 Matriz de Correlación":
    st.subheader("📊 Matriz de Correlación")
    corr_matrix = df_all[["ALLSKY_KT", "ALLSKY_SFC_SW_DWN"]].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar_kws={'label': 'Correlación'})
    st.pyplot(fig)

# Percentiles
elif menu == "🌡 Percentiles":
    st.subheader("📊 Mapa de Percentiles")
    percentil = st.sidebar.radio("Selecciona un Percentil", [50, 75])
    umbral = df_all['ALLSKY_KT'].quantile(percentil / 100)
    df_altos = df_all[df_all['ALLSKY_KT'] > umbral]
    df_bajos = df_all[df_all['ALLSKY_KT'] <= umbral]
    mapa = folium.Map(location=[df_all['LAT'].mean(), df_all['LON'].mean()], zoom_start=6)
    for _, row in df_altos.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LON']], radius=8, color="red",
            fill=True, fill_color="red", fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>ALLSKY_KT: {row['ALLSKY_KT']:.2f}"
        ).add_to(mapa)
    for _, row in df_bajos.iterrows():
        radius = 4 + (row['ALLSKY_KT'] / df_all['ALLSKY_KT'].max()) * 10
        folium.CircleMarker(
            location=[row['LAT'], row['LON']], radius=radius, color="blue",
            fill=True, fill_color="blue", fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>ALLSKY_KT: {row['ALLSKY_KT']:.2f}"
        ).add_to(mapa)
    st_folium(mapa, width=700, height=400)

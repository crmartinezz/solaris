import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import seaborn as sns
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium  # Importar la librería para usar folium en Streamlit

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Visualización de Datos Climáticos",
    page_icon="🌍",
    layout="wide"
)
st.title("🌍 Visualización de Datos Climáticos")
st.sidebar.title("🔍 Opciones de Navegación")

# Cargar el archivo CSV desde el proyecto
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_unificados.csv")
    return df

# Cargar los datos
df_all = cargar_datos()

# Crear una nueva columna 'Fecha' combinando 'YEAR', 'MO', 'DY'
df_all['Fecha'] = pd.to_datetime(df_all.astype(str).loc[:, ["YEAR", "MO", "DY"]].agg('-'.join, axis=1))

# Menú de navegación en la barra lateral
menu = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["Inicio", "Datos", "Visualización", "Matriz de Correlación", "Percentil 75", "Percentil 50", "Configuración"]
)

# Si el usuario selecciona "Datos", muestra los datos en formato de tabla
if menu == "Datos":
    st.subheader("📂 Datos Disponibles")
    st.dataframe(df_all)

# Si el usuario selecciona "Visualización", muestra los gráficos interactivos
elif menu == "Visualización":
    st.subheader("📊 Visualización de Datos Climáticos")

    # Filtro por año
    año = st.sidebar.selectbox("Selecciona el año", df_all["YEAR"].unique())
    df_filtrado = df_all[df_all["YEAR"] == año]

    st.write(f"Mostrando datos para el año: {año}")
    
    # Filtro por rango de fechas
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        [df_filtrado["Fecha"].min(), df_filtrado["Fecha"].max()]
    )

    # Filtrar los datos según el rango de fechas
    df_filtrado = df_filtrado[(df_filtrado["Fecha"] >= pd.to_datetime(fecha_inicio)) & (df_filtrado["Fecha"] <= pd.to_datetime(fecha_fin))]

    # Filtro por latitud y longitud
    latitudes_disponibles = df_filtrado["LAT"].unique()
    longitudes_disponibles = df_filtrado["LON"].unique()
    
    lat = st.sidebar.selectbox("Selecciona la latitud", latitudes_disponibles)
    lon = st.sidebar.selectbox("Selecciona la longitud", longitudes_disponibles)

    # Filtrar los datos según la latitud y longitud seleccionadas
    df_filtrado_lat_lon = df_filtrado[(df_filtrado["LAT"] == lat) & (df_filtrado["LON"] == lon)]
    
    # Crear un mapa con folium centrado en la latitud y longitud seleccionadas
    mapa = folium.Map(location=[lat, lon], zoom_start=10)
    
    # Añadir un marcador en la ubicación seleccionada
    folium.Marker(
        location=[lat, lon],
        popup=f"Lat: {lat}, Lon: {lon}",
        icon=folium.Icon(color="blue")
    ).add_to(mapa)

    # Mostrar el mapa en Streamlit
    st.subheader("🌍 Mapa de Ubicación")
    st_folium(mapa, width=700, height=400)
    
    # Crear gráfico interactivo de líneas con Plotly
    fig = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_KT"],
        title=f"All Sky Surface Shortwave Downward Irradiance (kW/m²/day) en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',  # Línea recta entre puntos
        template="plotly_dark"  # Establecer el tema oscuro
    )
    fig.update_traces(line=dict(color='red'))
    # Mostrar el gráfico interactivo
    st.plotly_chart(fig)

    # Crear gráfico interactivo de líneas con Plotly para ALLSKY_SFC_SW_DWN
    fig = px.line(
        df_filtrado_lat_lon,
        x="Fecha",
        y=["ALLSKY_SFC_SW_DWN"],
        title=f"All Sky Insolation Clearness Index en Lat: {lat} y Lon: {lon} en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',  # Línea recta entre puntos
        template="plotly_dark"  # Establecer el tema oscuro
    )

    # Mostrar el gráfico interactivo
    st.plotly_chart(fig)

# Si el usuario selecciona "Matriz de Correlación", muestra la matriz de correlación
elif menu == "Matriz de Correlación":
    st.subheader("📊 Matriz de Correlación de Variables Climáticas")
    
    # Calcular la matriz de correlación entre las variables
    corr_matrix = df_all[["ALLSKY_KT", "ALLSKY_SFC_SW_DWN"]].corr()
    
    # Mostrar la matriz de correlación como un mapa de calor utilizando seaborn
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar_kws={'label': 'Correlación'})
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

# Si el usuario selecciona "Configuración", muestra la configuración
elif menu == "Configuración":
    st.sidebar.success("🎉 Configuración completa")
    
elif menu == "Percentil 75":
    st.subheader("📊 Mapa con los valores más altos de All Sky Surface Shortwave Downward Irradiance")
    df_promedio = df_all.groupby(['LAT', 'LON'])['ALLSKY_KT'].mean().reset_index()
    percentil_75 = df_all['ALLSKY_KT'].quantile(0.75)
    df_puntos_altos = df_promedio[df_promedio['ALLSKY_KT'] > percentil_75]
    df_puntos_bajos = df_promedio[df_promedio['ALLSKY_KT'] <= percentil_75]
    mapa = folium.Map(location=[df_promedio['LAT'].mean(), df_promedio['LON'].mean()], zoom_start=6)

    for _, row in df_puntos_altos.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=8,  # Radio fijo para los puntos altos
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)
    for _, row in df_puntos_bajos.iterrows():
        # Asignar tamaño proporcional al valor de ALLSKY_KT
        radius = 4 + (row['ALLSKY_KT'] / df_promedio['ALLSKY_KT'].max()) * 10  # Escala de tamaño
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=radius,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)
    st.subheader("🌍 Mapa de Puntos Mayores y Menores al Percentil 75")
    st_folium(mapa, width=700, height=400)

elif menu == "Percentil 50":
    st.subheader("📊 Mapa con los valores más altos de All Sky Surface Shortwave Downward Irradiance")

    df_promedio = df_all.groupby(['LAT', 'LON'])['ALLSKY_KT'].mean().reset_index()
    percentil_50 = df_all['ALLSKY_KT'].quantile(0.50)
    df_puntos_altos = df_promedio[df_promedio['ALLSKY_KT'] > percentil_50]
    df_puntos_bajos = df_promedio[df_promedio['ALLSKY_KT'] <= percentil_50]
    mapa = folium.Map(location=[df_promedio['LAT'].mean(), df_promedio['LON'].mean()], zoom_start=6)
    for _, row in df_puntos_altos.iterrows():
        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=8,  # Radio fijo para los puntos altos
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)

    for _, row in df_puntos_bajos.iterrows():
        # Asignar tamaño proporcional al valor de ALLSKY_KT
        radius = 4 + (row['ALLSKY_KT'] / df_promedio['ALLSKY_KT'].max()) * 10  # Escala de tamaño

        folium.CircleMarker(
            location=[row['LAT'], row['LON']],
            radius=radius,
            color="blue",
            fill=True,
            fill_color="blue",
            fill_opacity=0.6,
            popup=f"Lat: {row['LAT']} - Lon: {row['LON']}<br>Promedio ALLSKY_KT: {row['ALLSKY_KT']:.2f}",
        ).add_to(mapa)

    st.subheader("🌍 Mapa de Puntos Mayores y Menores al Percentil 50")
    st_folium(mapa, width=700, height=400)

elif menu == "Configuración":
    st.subheader("🗣️🗣️🗣️ Alejandro no hace un hijueputa culo en los trabajos grupales")
# Ejecución del Script
if __name__ == "__main__":
    st.sidebar.info("Ejecuta este script con: streamlit run <nombre-del-script>.py")

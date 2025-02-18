import pandas as pd
import streamlit as st
import plotly.express as px

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
    ["Inicio", "Datos", "Visualización", "Configuración"]
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

    # Crear gráfico interactivo de líneas con Plotly
    fig = px.line(
        df_filtrado,
        x="Fecha",
        y=["ALLSKY_KT", "ALLSKY_SFC_SW_DWN"],
        title=f"Comparación entre ALLSKY_KT y ALLSKY_SFC_SW_DWN en el año {año}",
        labels={"Fecha": "Fecha", "value": "Valor", "variable": "Variable"},
        line_shape='linear',  # Línea recta entre puntos
        template="plotly_dark"  # Establecer el tema oscuro
    )

    # Mostrar el gráfico interactivo
    st.plotly_chart(fig)

# Si el usuario selecciona "Configuración", muestra la configuración
elif menu == "Configuración":
    st.sidebar.success("🎉 Configuración completa")

# 11. Ejecución del Script
if __name__ == "__main__":
    st.sidebar.info("Ejecuta este script con: streamlit run <nombre-del-script>.py")

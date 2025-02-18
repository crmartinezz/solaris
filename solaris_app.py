import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
#https://dbagro-m72dj8r2cwpkxyj7mi7wna.streamlit.app/ 
st.set_page_config(
    page_title="Base de Datos AgroColombiano",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Base de Datos AgroColombiano")
st.sidebar.title("🔍 Opciones de Navegación")

# Establecer semilla para reproducibilidad
np.random.seed(42)

# Generación de la base de datos
data_agro = pd.DataFrame({
    "Fecha": pd.date_range(start="2024-01-01", periods=150, freq="D"),
    "Producto": np.random.choice(["Café", "Banano", "Arroz", "Maíz", "Yuca", "Soya", "Caña de azúcar", "Papas"], size=150),
    "Cantidad_Producción": np.random.randint(1000, 10000, size=150),  # Cantidad de producción en kilogramos
    "Precio_Uni": np.random.uniform(1000, 3000, size=150),  # Precio unitario en COP
    "Descuento": np.random.uniform(5, 20, size=150),  # Descuento en porcentaje
    "Satisfacción": np.random.randint(1, 10, size=150),  # Satisfacción de los productores
    "Región": np.random.choice(["Antioquia", "Cundinamarca", "Santander", "Tolima", "Valle del Cauca", "Magdalena", "Nariño", "Cesar"], size=150),
    "Tipo_Clima": np.random.choice(["Tropical", "Templado", "Cálido", "Frío"], size=150)
})

menu = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["Inicio", "Datos", "Visualización", "Configuración"]
)

if menu == "Datos":
    st.subheader("📂 Datos Generados")
    st.dataframe(data_agro)

elif menu == "Visualización":
    st.subheader("📊 Visualización de Datos")

    # Filtro por Producto
    producto = st.sidebar.selectbox("Selecciona un producto", data_agro["Producto"].unique())
    filtered_data = data_agro[data_agro["Producto"] == producto]
    st.write(f"Mostrando datos para el producto: {producto}")
    st.dataframe(filtered_data)

    # Filtro por Cantidad de Producción
    cantidad_min, cantidad_max = st.sidebar.slider(
        "Selecciona el rango de cantidad de producción:",
        min_value=int(data_agro["Cantidad_Producción"].min()),
        max_value=int(data_agro["Cantidad_Producción"].max()),
        value=(int(data_agro["Cantidad_Producción"].min()), int(data_agro["Cantidad_Producción"].max()))
    )
    filtered_data = filtered_data[(filtered_data["Cantidad_Producción"] >= cantidad_min) & (filtered_data["Cantidad_Producción"] <= cantidad_max)]

    # Filtro por Fecha
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el rango de fechas:",
        [data_agro["Fecha"].min(), data_agro["Fecha"].max()],
        min_value=data_agro["Fecha"].min(),
        max_value=data_agro["Fecha"].max()
    )
    filtered_data = filtered_data[(filtered_data["Fecha"] >= pd.to_datetime(fecha_inicio)) & (filtered_data["Fecha"] <= pd.to_datetime(fecha_fin))]

    # Botón para Reiniciar Filtros
    if st.sidebar.button("Reiniciar Filtros"):
        filtered_data = data_agro
        st.experimental_rerun()

    # Implementar Pestañas
    st.subheader("📌 Navegación entre Pestañas")
    tab1, tab2 = st.tabs(["📊 Gráficos", "📂 Datos"])

    with tab1:
        st.subheader("Visualización de Datos")
        
        # Crear gráfico interactivo con Plotly
        fig_plotly = px.scatter(
            filtered_data,
            x="Cantidad_Producción",
            y="Precio_Uni",
            color="Región",  # Colorear por Región
            title="Relación entre Cantidad de Producción y Precio Unitario por Región",
            labels={"Cantidad_Producción": "Cantidad de Producción (kg)", "Precio_Uni": "Precio Unitario (COP)"},
            hover_data=["Producto", "Fecha"],  # Mostrar más información al pasar el mouse
            template="plotly_dark"  # Opcional: cambia el tema del gráfico
        )
        
        st.plotly_chart(fig_plotly)

    with tab2:
        st.subheader("Datos Crudos")
        st.dataframe(filtered_data)

elif menu == "Configuración":
    st.sidebar.success("🎉 Configuración completa")

# 11. Ejecución del Script
if __name__ == "__main__":
    st.sidebar.info("Ejecuta este script con: streamlit run talento-roadmap-app.py")

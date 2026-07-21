"""
10 Gráficas con Plotly — vehicles_us.csv (versión Streamlit)
================================================================
App de una sola vista:
  - Título y subtítulo
  - Tabla interactiva (manipulable) con los principales estadísticos
  - Las 10 visualizaciones de Plotly

Cómo correr:
  streamlit run streamlit_10_graficas.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------------------------------
# CONFIGURACIÓN Y CARGA DE DATOS
# -------------------------------------------------------------------------
st.set_page_config(page_title="Sprint7: Aplicativo web con streamlit", layout="wide")

st.title("Sprint7: Aplicativo web con streamlit")
st.title("Análisis y visualización de datos vehiculares")
st.subheader("Desarrollado por Isaac Noriega")


@st.cache_data
def load_data():
    df = pd.read_csv("vehicles_us.csv")
    df["manufacturer"] = df["model"].astype(str).str.split().str[0]
    df["date_posted"] = pd.to_datetime(df["date_posted"], errors="coerce")
    df["is_4wd_label"] = df["is_4wd"].apply(lambda x: "4x4" if x == 1.0 else "No 4x4")
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "No se encontró `vehicles_us.csv` en el directorio del proyecto. "
        "Coloca el archivo junto a este script y recarga la página."
    )
    st.stop()

# -------------------------------------------------------------------------
# TABLA INTERACTIVA CON LOS PRINCIPALES ESTADÍSTICOS
# -------------------------------------------------------------------------
# st.dataframe ya es "manipulable" por sí mismo: permite ordenar por columna,
# redimensionar y buscar sobre los resultados sin escribir código adicional.
st.dataframe(df.describe(include="all").T, use_container_width=True)

st.divider()

# -------------------------------------------------------------------------
# 1. Histograma de días en el mercado (days_listed)
# -------------------------------------------------------------------------
st.markdown("### 1. Distribución de días que un anuncio permanece publicado")
fig1 = px.histogram(
    df, x="days_listed", nbins=40, marginal="box",
    title="Distribución de días que un anuncio permanece publicado",
)
st.plotly_chart(fig1, use_container_width=True)

# -------------------------------------------------------------------------
# 2. Boxplot de precio por tipo de combustible
# -------------------------------------------------------------------------
st.markdown("### 2. Precio por tipo de combustible")
fig2 = px.box(
    df, x="fuel", y="price", color="fuel",
    title="Precio por tipo de combustible",
)
fig2.update_layout(showlegend=False)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------------------------------
# 3. Matriz de dispersión (scatter matrix / SPLOM)
# -------------------------------------------------------------------------
st.markdown("### 3. Matriz de dispersión: price, odometer, cylinders, model_year, days_listed")
fig3 = px.scatter_matrix(
    df,
    dimensions=["price", "odometer", "cylinders", "model_year", "days_listed"],
    color="fuel",
    title="Matriz de dispersión: price, odometer, cylinders, model_year, days_listed",
    opacity=0.4,
)
fig3.update_traces(diagonal_visible=False)
st.plotly_chart(fig3, use_container_width=True)

# -------------------------------------------------------------------------
# 4. Barras compuestas: conteo de anuncios por fabricante y tipo de combustible
# -------------------------------------------------------------------------
st.markdown("### 4. Conteo de anuncios por fabricante, compuesto por tipo de combustible")
top_fabricantes_bar = df["manufacturer"].value_counts().head(15).index.tolist()
df_fab_fuel = df[df["manufacturer"].isin(top_fabricantes_bar)]
conteo_fab_fuel = df_fab_fuel.groupby(["manufacturer", "fuel"]).size().reset_index(name="conteo")
fig4 = px.bar(
    conteo_fab_fuel, x="manufacturer", y="conteo", color="fuel",
    barmode="stack",
    category_orders={"manufacturer": top_fabricantes_bar},
    title="Conteo de anuncios por fabricante (top 15), compuesto por tipo de combustible",
)
st.plotly_chart(fig4, use_container_width=True)

# -------------------------------------------------------------------------
# 5. Barras apiladas: transmisión por tipo de vehículo
# -------------------------------------------------------------------------
st.markdown("### 5. Distribución de transmisión por tipo de vehículo")
trans_por_tipo = df.groupby(["type", "transmission"]).size().reset_index(name="conteo")
fig5 = px.bar(
    trans_por_tipo, x="type", y="conteo", color="transmission",
    title="Distribución de transmisión por tipo de vehículo",
    barmode="stack",
)
st.plotly_chart(fig5, use_container_width=True)

# -------------------------------------------------------------------------
# 6. Treemap: fabricante y tipo de vehículo
# -------------------------------------------------------------------------
st.markdown("### 6. Treemap: top 10 fabricantes y su composición por tipo")
top_fabricantes = df["manufacturer"].value_counts().head(10).index
df_tree = df[df["manufacturer"].isin(top_fabricantes)]
fig6 = px.treemap(
    df_tree, path=["manufacturer", "type"],
    title="Treemap: top 10 fabricantes y su composición por tipo de vehículo",
)
st.plotly_chart(fig6, use_container_width=True)

# -------------------------------------------------------------------------
# 7. Sunburst: número de cilindros > tipo de combustible
# -------------------------------------------------------------------------
st.markdown("### 7. Jerarquía: número de cilindros > tipo de combustible")
df_cil = df.dropna(subset=["cylinders"]).copy()
df_cil["cylinders_label"] = df_cil["cylinders"].astype(int).astype(str) + " cilindros"
fig7 = px.sunburst(
    df_cil, path=["cylinders_label", "fuel"],
    title="Jerarquía: número de cilindros > tipo de combustible",
)
st.plotly_chart(fig7, use_container_width=True)

# -------------------------------------------------------------------------
# 8. Conteo de anuncios por condición y transmisión, según combustible
# -------------------------------------------------------------------------
st.markdown("### 8. Conteo de anuncios por condición y transmisión, según tipo de combustible")
conteo_cond_trans = (
    df.groupby(["fuel", "type", "transmission"]).size().reset_index(name="conteo")
)
fig8 = px.bar(
    conteo_cond_trans, x="type", y="conteo", color="transmission",
    facet_col="fuel", facet_col_wrap=3, barmode="group",
    title="Conteo de anuncios por condición y transmisión, según tipo de combustible",
)
fig8.update_xaxes(tickangle=45)
st.plotly_chart(fig8, use_container_width=True)

# -------------------------------------------------------------------------
# 9. Precio promedio por mes de publicación
# -------------------------------------------------------------------------
st.markdown("### 9. Precio promedio de anuncios por mes de publicación")
df_mes = df.dropna(subset=["date_posted"]).copy()
df_mes["mes"] = df_mes["date_posted"].dt.to_period("M").dt.to_timestamp()
precio_mensual = df_mes.groupby("mes")["price"].mean().reset_index()
fig9 = px.line(
    precio_mensual, x="mes", y="price", markers=True,
    title="Precio promedio de anuncios por mes de publicación",
    labels={"mes": "mes", "price": "precio promedio"},
)
st.plotly_chart(fig9, use_container_width=True)

# -------------------------------------------------------------------------
# 10. Colores de pintura más comunes
# -------------------------------------------------------------------------
st.markdown("### 10. Anuncios por color de pintura")
color_counts = df["paint_color"].value_counts().reset_index()
color_counts.columns = ["paint_color", "conteo"]
fig10 = px.bar(
    color_counts, x="conteo", y="paint_color", orientation="h",
    title="Anuncios por color de pintura",
)
fig10.update_yaxes(categoryorder="total ascending")
st.plotly_chart(fig10, use_container_width=True)
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="auto",
)

# Filtros de mes y año
year = st.sidebar.selectbox("Seleccione el año", list(range(2020, 2025)))
month = st.sidebar.selectbox("Seleccione el mes", ["Todos"] + list(range(1, 13)))
if month == "Todos":
    month = None

# URL base de FastAPI
base_url = os.getenv("BASE_URL")


def fetch_scalar_data(endpoint, month, year):
    params = {"month": month, "year": year}
    response = requests.get(f"{base_url}/{endpoint}", params=params)

    # Verifica el código de estado y el contenido antes de intentar decodificar como JSON
    if (
        response.status_code == 200 and response.text.strip()
    ):  # Asegura que no esté vacío
        try:
            data = response.json()
            # Si el resultado es un diccionario con un valor escalar, devuelve solo el valor
            if isinstance(data, dict) and len(data) == 1:
                return list(data.values())[0]  # Obtén el único valor en el diccionario
            else:
                st.error("Formato de respuesta inesperado.")
        except ValueError:
            st.error("Error de formato: no se puede decodificar JSON.")
    else:
        st.warning("No hay datos para el año consultado.")
        return None  # Retorna None si no hay datos


# Función para obtener datos del API
def fetch_dashboard_data(endpoint, month, year):
    params = {"month": month, "year": year}
    response = requests.get(f"{base_url}/{endpoint}", params=params)
    data = response.json()
    return pd.DataFrame(data)  # Convierte el listado de datos en un DataFrame


# Crea tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Inicio",
        "Clientes",
        "Proveedores",
        "Vendedores",
        "Productos",
        "Ventas",
        "Compras",
    ]
)


with tab1:
    st.header("Bienvenido al dashboard")

    # Obtiene todas las ventas del sistema
    sales_array = fetch_dashboard_data("sales", month, year)
    if sales_array is not None:
        # Obtiene las ventas del año seleccionado
        # Obtiene encabezados y calcula las metricas de ventas
        if month is None:
            title_header = f"Ventas del año {year}"
            total_sales = sales_array["total_sales"].filter(year_concept=year).sum()
            average_sales = sales_array["total_sales"].filter(year_concept=year).mean()
            median_sales = sales_array["total_sales"].filter(year_concept=year).median()
            max_sales = sales_array["total_sales"].filter(year_concept=year).max()
            min_sales = sales_array["total_sales"].filter(year_concept=year).min()

        else:
            # Obtiene las ventas filtradas por mes y año
            title_header = f"Ventas del mes {month} del año {year}"
            total_sales = (
                sales_array["total_sales"]
                .filter(month_concept=month, year_concept=year)
                .sum()
            )
            average_sales = (
                sales_array["total_sales"]
                .filter(month_concept=month, year_concept=year)
                .mean()
            )
            median_sales = (
                sales_array["total_sales"]
                .filter(month_concept=month, year_concept=year)
                .median()
            )
            max_sales = (
                sales_array["total_sales"]
                .filter(month_concept=month, year_concept=year)
                .max()
            )
            min_sales = (
                sales_array["total_sales"]
                .filter(month_concept=month, year_concept=year)
                .min()
            )

        st.header(title_header)
        # Calcula métricas de ventas

        st.header(f"{title_header} $ {total_sales:,.2f}")
        st.header(f"Promedio de {title_header}: $ {average_sales:,.2f}")
        st.header(f"Mediana de {title_header}: $ {median_sales:,.2f}")
        st.header(f"Maximo de {title_header}: $ {max_sales:,.2f}")
        st.header(
            f"Minimo de {title_header}: $ {min_sales:,.2f}"
        )  # Muestra los datos de las ventas

    else:  # Si no hay datos, muestra un mensaje de advertencia
        st.warning("No hay datos de ventas disponibles")


with tab2:
    # Obtener total de ventas
    total_sales = fetch_scalar_data("total_sales", None, year)
    if total_sales is not None:
        st.header(f"Total de ventas anuales: $ {total_sales:,.2f}")
    else:
        st.warning("No hay datos de ventas disponibles")

    st.header("Los 5 primeros mejores clientes")
    # Mostrar Top 5 Clientes
    top_clients = fetch_dashboard_data("top_clients", month, year)

    if top_clients.empty:
        st.warning("No hay datos para mostrar")
    else:
        st.dataframe(
            top_clients.style.format(formatter={"total": "$ {:,.2f}"}),
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn(label="Cliente"),
                "total": st.column_config.NumberColumn(label="Ventas"),
            },
        )

        st.header(f"Suma de las Ventas: $ {top_clients['total'].sum():,.2f}")

        fig, ax = plt.subplots()
        ax.pie(top_clients["total"], labels=top_clients["name"], autopct="%1.1f%%")
        st.pyplot(fig)

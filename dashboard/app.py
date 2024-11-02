import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

initial_year = int(os.getenv("INITIAL_YEAR"))
final_year = datetime.now().year


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


def calculate_delta(previous_value, last_value, divisor: int):
    return round(
        (
            (round(last_value / divisor, 2) - round(previous_value / divisor, 2))
            / round(previous_value / divisor, 2)
        )
        * 100,
        2,
    )


def get_metric(title: str, mount_df, metric_label: str, delta_df, divisor: int):
    return st.metric(
        label=title,
        value=f"{round(mount_df/divisor,2)} {metric_label}",
        delta=f"{delta_df} %" if delta_df is not None else None,
    )


# Filtra por el año, agrupa por name, suma total_sales, y ordena descendente para tomar el top 5
def get_top(filtered_df, group_column: str, mount_column: str):
    df = (
        filtered_df.groupby(group_column, as_index=False)[mount_column]
        .sum()
        .sort_values(by=mount_column, ascending=False)
        .head(5)
    )
    return df


def format_top_dataframe(
    df,
    subject_column: str,
    mount_column: str,
    subject_label: str,
    mount_label: str,
):
    formated_df = st.dataframe(
        df.style.format(formatter={mount_column: "$ {:,.2f}"}),
        hide_index=True,
        column_config={
            subject_column: st.column_config.TextColumn(label=subject_label),
            mount_column: st.column_config.NumberColumn(label=mount_label),
        },
    )
    return formated_df


def get_circular_graph(df, mount_column: str, subject_column: str):
    fig, ax = plt.subplots()
    ax.pie(df[mount_column], labels=df[subject_column], autopct="%1.1f%%")
    st.pyplot(fig)


st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="auto",
)

st.header("Bienvenido al dashboard")

# Filtros de mes y año
year = st.sidebar.selectbox(
    "Seleccione el año", list(range(initial_year, final_year + 1))
)
month = st.sidebar.selectbox("Seleccione el mes", ["Todos"] + list(range(1, 13)))
if month == "Todos":
    month = None

# URL base de FastAPI
base_url = os.getenv("BASE_URL")

# Obtiene todas las ventas del sistema
sales_array = fetch_dashboard_data("sales", month, year)
if sales_array is not None:
    # Obtiene las ventas del año seleccionado
    # Obtiene encabezados y calcula las metricas de ventas
    if month is None:
        title_header = f"Ventas del año {year}"
        # Filtra las filas en las que el año coincide
        sales_array_filtered = sales_array[sales_array["year_concept"] == year]
        total_sales = sales_array_filtered["total_sales"].sum()
        average_sales = sales_array_filtered["total_sales"].mean()
        median_sales = sales_array_filtered["total_sales"].median()
        max_sales = sales_array_filtered["total_sales"].max()
        min_sales = sales_array_filtered["total_sales"].min()
        number_of_sales = sales_array_filtered["total_sales"].count()
    else:
        title_header = f"Ventas del mes del año {year}"
        # Filtra filas en las que el mes y el año coinciden
        sales_array_filtered = sales_array[
            (sales_array["month_concept"] == month)
            & (sales_array["year_concept"] == year)
        ]
        total_sales = sales_array_filtered["total_sales"].sum()
        average_sales = sales_array_filtered["total_sales"].mean()
        median_sales = sales_array_filtered["total_sales"].median()
        max_sales = sales_array_filtered["total_sales"].max()
        min_sales = sales_array_filtered["total_sales"].min()
        number_of_sales = sales_array_filtered["total_sales"].count()

else:  # Si no hay datos, muestra un mensaje de advertencia
    st.warning("No hay datos de ventas disponibles")


# Obtiene todas las compras del sistema
purchases_array = fetch_dashboard_data("purchases", month, year)
if purchases_array is not None:
    # Obtiene las ventas del año seleccionado
    # Obtiene encabezados y calcula las metricas de ventas
    if month is None:
        title_header_purchases = f"Compras del año {year}"
        # Filtra las filas en las que el año coincide
        purchases_array_filtered = purchases_array[
            purchases_array["year_concept"] == year
        ]
        total_purchases = purchases_array_filtered["total_purchases"].sum()
        average_purchases = purchases_array_filtered["total_purchases"].mean()
        median_purchases = purchases_array_filtered["total_purchases"].median()
        max_purchases = purchases_array_filtered["total_purchases"].max()
        min_purchases = purchases_array_filtered["total_purchases"].min()
        number_of_purchases = purchases_array_filtered["total_purchases"].count()

    else:
        title_header_purchases = f"Compras del mes del año {year}"
        # Filtra filas en las que el mes y el año coinciden
        purchases_array_filtered = purchases_array[
            (purchases_array["month_concept"] == month)
            & (purchases_array["year_concept"] == year)
        ]
        total_purchases = purchases_array_filtered["total_purchases"].sum()
        average_purchases = purchases_array_filtered["total_purchases"].mean()
        median_purchases = purchases_array_filtered["total_purchases"].median()
        max_purchases = purchases_array_filtered["total_purchases"].max()
        min_purchases = purchases_array_filtered["total_purchases"].min()
        number_of_purchases = purchases_array_filtered["total_purchases"].count()

else:  # Si no hay datos, muestra un mensaje de advertencia
    st.warning("No hay datos de compras disponibles")


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
    # Calcula métricas de ventas
    delta_sales = None
    delta_average_sales = None
    delta_median_sales = None
    delta_max_sales = None
    delta_min_sales = None
    delta_number_of_sales = None
    sales_array_filtered_previous = None

    if year == initial_year:
        if month is not None:
            if month > 1:
                sales_array_filtered_previous = sales_array[
                    (sales_array["month_concept"] == month - 1)
                    & (sales_array["year_concept"] == year)
                ]
    else:
        if month is None:
            sales_array_filtered_previous = sales_array[
                sales_array["year_concept"] == year - 1
            ]
        else:
            if month == 1:
                sales_array_filtered_previous = sales_array[
                    (sales_array["month_concept"] == 12)
                    & (sales_array["year_concept"] == year - 1)
                ]
            else:
                sales_array_filtered_previous = sales_array[
                    (sales_array["month_concept"] == month - 1)
                    & (sales_array["year_concept"] == year)
                ]

        previous_total_sales = sales_array_filtered_previous["total_sales"].sum()
        delta_sales = calculate_delta(previous_total_sales, total_sales, 1000)

        previous_average_sales = sales_array_filtered_previous["total_sales"].mean()
        delta_average_sales = calculate_delta(
            previous_average_sales, average_sales, 1000
        )

        previous_median_sales = sales_array_filtered_previous["total_sales"].median()
        delta_median_sales = calculate_delta(previous_median_sales, median_sales, 1000)

        previous_max_sales = sales_array_filtered_previous["total_sales"].max()
        delta_max_sales = calculate_delta(previous_max_sales, max_sales, 1000)

        previous_min_sales = sales_array_filtered_previous["total_sales"].min()
        delta_min_sales = calculate_delta(previous_min_sales, min_sales, 1000)

        previous_number_of_sales = sales_array_filtered_previous["total_sales"].count()
        delta_number_of_sales = calculate_delta(
            previous_number_of_sales, number_of_sales, 1
        )

    col1, col2 = st.columns(2)
    with col1:
        get_metric("Ventas", total_sales, "mdp", delta_sales, 1000)
    with col2:
        get_metric("Ventas Promedio", average_sales, "mdp", delta_average_sales, 1000)

    col3, col4 = st.columns(2)
    with col3:
        get_metric("Mediana Ventas", median_sales, "mdp", delta_median_sales, 1000)
    with col4:
        get_metric("Maxima Venta", max_sales, "mdp", delta_max_sales, 1000)

    col5, col6 = st.columns(2)
    with col5:
        get_metric("Minima Venta", min_sales, "mdp", delta_min_sales, 1000)
    with col6:
        get_metric(
            "Número de ventas", number_of_sales, "facturas", delta_number_of_sales, 1
        )

    # Calcula métricas de compras
    delta_purchases = None
    delta_average_purchases = None
    delta_median_purchases = None
    delta_max_purchases = None
    delta_min_purchases = None
    delta_number_of_purchases = None
    purchases_array_filtered_previous = None

    if year == initial_year:
        if month is not None:
            if month > 1:
                purchases_array_filtered_previous = purchases_array[
                    (purchases_array["month_concept"] == month - 1)
                    & (purchases_array["year_concept"] == year)
                ]
    else:
        if month is None:
            purchases_array_filtered_previous = purchases_array[
                purchases_array["year_concept"] == year - 1
            ]
        else:
            if month == 1:
                purchases_array_filtered_previous = purchases_array[
                    (purchases_array["month_concept"] == 12)
                    & (purchases_array["year_concept"] == year - 1)
                ]
            else:
                purchases_array_filtered_previous = purchases_array[
                    (purchases_array["month_concept"] == month - 1)
                    & (purchases_array["year_concept"] == year)
                ]

        previous_total_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].sum()
        delta_purchases = calculate_delta(
            previous_total_purchases, total_purchases, 1000
        )

        previous_average_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].mean()
        delta_average_purchases = calculate_delta(
            previous_average_purchases, average_purchases, 1000
        )

        previous_median_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].median()
        delta_median_purchases = calculate_delta(
            previous_median_purchases, median_purchases, 1000
        )

        previous_max_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].max()
        delta_max_purchases = calculate_delta(
            previous_max_purchases, max_purchases, 1000
        )

        previous_min_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].min()
        delta_min_purchases = calculate_delta(
            previous_min_purchases, min_purchases, 1000
        )

        previous_number_of_purchases = purchases_array_filtered_previous[
            "total_purchases"
        ].count()
        delta_number_of_purchases = calculate_delta(
            previous_number_of_purchases, number_of_purchases, 1
        )

    col7, col8 = st.columns(2)
    with col7:
        get_metric("Compras", total_purchases, "mdp", delta_purchases, 1000)
    with col8:
        get_metric(
            "Compras Promedio", average_purchases, "mdp", delta_average_purchases, 1000
        )

    col9, col10 = st.columns(2)
    with col9:
        get_metric(
            "Mediana Compras", median_purchases, "mdp", delta_median_purchases, 1000
        )
    with col10:
        get_metric("Maxima Compra", max_purchases, "mdp", delta_max_purchases, 1000)

    col11, col12 = st.columns(2)
    with col11:
        get_metric("Minima Compra", min_purchases, "mdp", delta_min_purchases, 1000)
    with col12:
        get_metric(
            "Número de Compras",
            number_of_purchases,
            "compras",
            delta_number_of_purchases,
            1,
        )


with tab2:
    # Obtener total de ventas
    if total_sales is not None:
        st.header(f"{title_header} $ {total_sales:,.2f}")
    else:
        st.warning("No hay datos de ventas disponibles")

    st.header("Los 5 primeros mejores clientes")
    # Mostrar Top 5 Clientes
    top_clients = get_top(sales_array_filtered, "name", "total_sales")

    left_section, right_section = st.columns(2)
    if top_clients.empty:
        st.warning("No hay datos para mostrar")
    else:
        with left_section:
            df_formated = format_top_dataframe(
                top_clients, "name", "total_sales", "Cliente", "Ventas"
            )
    with right_section:
        with st.popover("Mostrar gráfica"):
            get_circular_graph(top_clients, "total_sales", "name")

with tab3:
    # Obtener total de compras
    if total_purchases is not None:
        st.header(f"{title_header_purchases} $ {total_purchases:,.2f}")
    else:
        st.warning("No hay datos de ventas disponibles")

    st.header("Los 5 primeros mejores proveedores")
    # Mostrar Top 5 Provvedores
    top_providers = get_top(purchases_array_filtered, "name", "total_purchases")

    left_section, right_section = st.columns([0.7, 0.3])
    if top_providers.empty:
        st.warning("No hay datos para mostrar")
    else:
        with left_section:
            df_formated = format_top_dataframe(
                top_providers, "name", "total_purchases", "Proveedor", "Compras"
            )
    with right_section:
        with st.popover("Mostrar gráfica"):
            get_circular_graph(top_providers, "total_purchases", "name")

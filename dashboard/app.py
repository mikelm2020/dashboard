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


# Función para obtener datos del API
@st.cache_data
def fetch_dashboard_data(endpoint):
    response = requests.get(f"{base_url}/{endpoint}")
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


def get_delta(
    number_month: int,
    number_year: int,
    concept_array,
    mount_column: str,
    last_value,
    divisor: int,
    delta_type: str,
):
    delta = None
    concept_array_filtered_previous = None

    if number_year == initial_year:
        if number_month is not None:
            if number_month > 1:
                concept_array_filtered_previous = concept_array[
                    (concept_array["month_concept"] == number_month - 1)
                    & (concept_array["year_concept"] == number_year)
                ]
    else:
        if number_month is None:
            concept_array_filtered_previous = concept_array[
                concept_array["year_concept"] == number_year - 1
            ]
        else:
            if number_month == 1:
                concept_array_filtered_previous = concept_array[
                    (concept_array["month_concept"] == 12)
                    & (concept_array["year_concept"] == number_year - 1)
                ]
            else:
                concept_array_filtered_previous = concept_array[
                    (concept_array["month_concept"] == number_month - 1)
                    & (concept_array["year_concept"] == number_year)
                ]
        if delta_type == "sum":
            previous_value = concept_array_filtered_previous[mount_column].sum()
        elif delta_type == "mean":
            previous_value = concept_array_filtered_previous[mount_column].mean()
        elif delta_type == "median":
            previous_value = concept_array_filtered_previous[mount_column].median()
        elif delta_type == "max":
            previous_value = concept_array_filtered_previous[mount_column].max()
        elif delta_type == "min":
            previous_value = concept_array_filtered_previous[mount_column].min()
        elif delta_type == "count":
            previous_value = concept_array_filtered_previous[mount_column].count()

        delta = calculate_delta(previous_value, last_value, divisor)

        return delta


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
    is_mount_format: bool = True,
):
    formated_df = st.dataframe(
        df.style.format(
            formatter={mount_column: "$ {:,.2f}" if is_mount_format else "{:,.0f}"}
        ),
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
sales_array = fetch_dashboard_data("sales")

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
purchases_array = fetch_dashboard_data("purchases")
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


# Obtiene todas las ventas por vendedor del sistema
sales_by_seller_array = fetch_dashboard_data("sellers")
if sales_by_seller_array is not None:
    # Obtiene las ventas del año seleccionado
    # Obtiene encabezados
    if month is None:
        title_header_seller = f"Ventas del año {year}"
        # Filtra las filas en las que el año coincide
        sales_by_seller_array_filtered = sales_by_seller_array[
            sales_by_seller_array["year_concept"] == year
        ]
        total_sales_by_seller = sales_by_seller_array_filtered["total_sales"].sum()
    else:
        title_header_seller = f"Ventas del mes del año {year}"
        # Filtra filas en las que el mes y el año coinciden
        sales_by_seller_array_filtered = sales_by_seller_array[
            (sales_by_seller_array["month_concept"] == month)
            & (sales_by_seller_array["year_concept"] == year)
        ]
        total_sales_by_seller = sales_by_seller_array_filtered["total_sales"].sum()

# Obtiene todas las ventas por producto del sistema
sales_by_product_array = fetch_dashboard_data("products")
if sales_by_product_array is not None:
    # Obtiene las ventas del año seleccionado
    # Obtiene encabezados
    if month is None:
        title_header_products = f"Volumen de Ventas del año {year}"
        # Filtra las filas en las que el año coincide
        sales_by_product_array_filtered = sales_by_product_array[
            sales_by_product_array["year_concept"] == year
        ]
        total_qty_by_product = sales_by_product_array_filtered["total_qty"].sum()
    else:
        title_header_products = f"Volumen de Ventas del mes del año {year}"
        # Filtra filas en las que el mes y el año coinciden
        sales_by_product_array_filtered = sales_by_product_array[
            (sales_by_product_array["month_concept"] == month)
            & (sales_by_product_array["year_concept"] == year)
        ]
        total_qty_by_product = sales_by_product_array_filtered["total_qty"].sum()

# Obtiene el margen bruto de ganancia
gross_profit_margin_array = fetch_dashboard_data("gross-profit-margin")
if gross_profit_margin_array is not None:
    # Obtiene las ventas del año seleccionado
    # Obtiene encabezados
    if month is None:
        title_header_gpm = f"Margen de Ganancia Bruta del año {year}"
        # Filtra las filas en las que el año coincide
        gross_profit_margin_array_filtered = gross_profit_margin_array[
            gross_profit_margin_array["year_concept"] == year
        ]
        total_gpm = gross_profit_margin_array_filtered["total_gpm"].sum()
    else:
        title_header_gpm = f"Volumen de Ventas del mes del año {year}"
        # Filtra filas en las que el mes y el año coinciden
        gross_profit_margin_array_filtered = gross_profit_margin_array[
            (gross_profit_margin_array["month_concept"] == month)
            & (gross_profit_margin_array["year_concept"] == year)
        ]
        total_gpm = gross_profit_margin_array_filtered["total_gpm"].sum()

# Crea tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Inicio",
        "Clientes",
        "Proveedores",
        "Vendedores",
        "Productos",
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

    delta_sales = get_delta(
        month, year, sales_array, "total_sales", total_sales, 1000, "sum"
    )

    delta_average_sales = get_delta(
        month, year, sales_array, "total_sales", average_sales, 1000, "mean"
    )

    delta_median_sales = get_delta(
        month, year, sales_array, "total_sales", median_sales, 1000, "median"
    )

    delta_max_sales = get_delta(
        month, year, sales_array, "total_sales", max_sales, 1000, "max"
    )

    delta_min_sales = get_delta(
        month, year, sales_array, "total_sales", min_sales, 1000, "min"
    )

    delta_number_of_sales = get_delta(
        month, year, sales_array, "total_sales", number_of_sales, 1, "count"
    )

    col1, col2 = st.columns(2)
    with col1:
        get_metric("Ingresos Netos", total_sales, "mdp", delta_sales, 1000)
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
            "Volumen de ventas", number_of_sales, "facturas", delta_number_of_sales, 1
        )

    # Calcula métricas de compras
    delta_purchases = None
    delta_average_purchases = None
    delta_median_purchases = None
    delta_max_purchases = None
    delta_min_purchases = None
    delta_number_of_purchases = None
    purchases_array_filtered_previous = None

    delta_purchases = get_delta(
        month, year, purchases_array, "total_purchases", total_purchases, 1000, "sum"
    )

    delta_average_purchases = get_delta(
        month, year, purchases_array, "total_purchases", average_purchases, 1000, "mean"
    )

    delta_median_purchases = get_delta(
        month,
        year,
        purchases_array,
        "total_purchases",
        median_purchases,
        1000,
        "median",
    )

    delta_max_purchases = get_delta(
        month, year, purchases_array, "total_purchases", max_purchases, 1000, "max"
    )

    delta_min_purchases = get_delta(
        month, year, purchases_array, "total_purchases", min_purchases, 1000, "min"
    )

    delta_number_of_purchases = get_delta(
        month, year, purchases_array, "total_purchases", number_of_purchases, 1, "count"
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
            "Volumen de Compras",
            number_of_purchases,
            "compras",
            delta_number_of_purchases,
            1,
        )

    # Calcula métricas
    delta_gross_profit_margin = None
    sales_array_filtered_previous = None

    delta_gross_profit_margin = get_delta(
        month, year, gross_profit_margin_array, "total_gpm", total_gpm, 1000, "sum"
    )

    col13, col14 = st.columns(2)
    with col13:
        get_metric(
            "Margen de Ganancia Bruta",
            total_gpm,
            "mdp",
            delta_gross_profit_margin,
            1000,
        )

with tab2:
    # Obtener total de ventas
    if total_sales is not None:
        st.header(f"{title_header}: $ {total_sales:,.2f}")
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
        st.header(f"{title_header_purchases}: $ {total_purchases:,.2f}")
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

with tab4:
    # Obtener total de ventas por vendedor
    if total_sales_by_seller is not None:
        st.header(f"{title_header_seller}: $ {total_sales_by_seller:,.2f}")
    else:
        st.warning("No hay datos de ventas disponibles")

    st.header("Los 5 primeros mejores vendedores")
    # Mostrar Top 5 Vendedores
    top_sellers = get_top(sales_by_seller_array_filtered, "name", "total_sales")

    left_section, right_section = st.columns(2)
    if top_sellers.empty:
        st.warning("No hay datos para mostrar")
    else:
        with left_section:
            df_formated = format_top_dataframe(
                top_sellers, "name", "total_sales", "Vendedor", "Ventas"
            )
    with right_section:
        with st.popover("Mostrar gráfica"):
            get_circular_graph(top_sellers, "total_sales", "name")

with tab5:
    # Obtener total de ventas por producto
    if total_qty_by_product is not None:
        st.header(f"{title_header_products}:  {total_qty_by_product:,.0f}")
    else:
        st.warning("No hay datos de ventas disponibles")

    st.header("Los 5 primeros mejores productos")
    # Mostrar Top 5 Productos
    top_products = get_top(sales_by_product_array_filtered, "name", "total_qty")

    left_section, right_section = st.columns([0.7, 0.3])
    if top_products.empty:
        st.warning("No hay datos para mostrar")
    else:
        with left_section:
            df_formated = format_top_dataframe(
                top_products, "name", "total_qty", "Producto", "Cantidad", False
            )
    with right_section:
        with st.popover("Mostrar gráfica"):
            get_circular_graph(top_products, "total_qty", "name")

import base64
import os
from datetime import datetime

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# FastAPI Base URL
base_url = os.getenv("BASE_URL")

initial_year = int(os.getenv("INITIAL_YEAR"))
final_year = datetime.now().year
number_of_databases = int(os.getenv("NUMBER_OF_DATABASES"))
number_of_entries = int(os.getenv("TOP_N"))


# Convertir la imagen local a base64
def image_to_base64(image_path):
    """
    Reads an image file and converts it to a base64 encoded string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """

    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def render_header(company_name, user_name, logo_base64):
    """
    Renders a header at the top of the page with the company name and the user name.

    Args:
        company_name (str): The name of the company.
        user_name (str): The name of the user.
        logo_base64 (str): The URL of the logo image.
    """
    # Contenedor del header
    with st.container():
        # Aplicar estilos al contenedor completo
        st.markdown(
            f"""
            <div style="
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                background-color: #262730; 
                padding: 10px 20px; 
                border-radius: 5px;">
                <div style="margin-right: 15px;">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 75px;">
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; font-size: 14px; font-weight: bold; color: #FFFFFF;">
                        {user_name}
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #c3edfa;">
                        {company_name}
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Function to get data from the API
@st.cache_data
def fetch_dashboard_data(endpoint: str, db_number: int):
    """Fetches data from the dashboard API and returns it as a pandas DataFrame.

    Args:
        endpoint (str): The API endpoint to fetch data from.
        db_number (int): The database number to fetch data from.

    Returns:
        pd.DataFrame: The fetched data, converted into a pandas DataFrame.
    """
    param = {"db_number": db_number}
    response = requests.get(f"{base_url}/{endpoint}", params=param)
    data = response.json()
    return pd.DataFrame(data)  # Convert the data list into a DataFrame


def calculate_delta(previous_value: float, last_value: float, divisor: int):
    """
    Calculates the percentage difference between two values.

    Args:
        previous_value (float): The value of the previous period.
        last_value (float): The value of the current period.
        divisor (int): A divisor to apply to both values, e.g. 1000 to get thousands.

    Returns:
        float: The percentage difference between the two values, rounded to 2 decimal places.
    """

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
    concept_array: pd.DataFrame,
    mount_column: str,
    last_value: float,
    divisor: int,
    delta_type: str,
):
    """
    Calculates the percentage difference between two values, given a divisor and a type of calculation.

    Args:
        number_month (int): The month of the current period.
        number_year (int): The year of the current period.
        concept_array (pd.DataFrame): The DataFrame containing the data to calculate the delta.
        mount_column (str): The name of the column to calculate the delta on.
        last_value (float): The value of the current period.
        divisor (int): A divisor to apply to both values, e.g. 1000 to get thousands.
        delta_type (str): The type of calculation to perform. Can be one of "sum", "mean", "median", "max", "min", or "count".

    Returns:
        float: The percentage difference between the two values, rounded to 2 decimal places.
    """

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
        elif delta_type == "nunique":
            previous_value = concept_array_filtered_previous[mount_column].nunique()

        delta = calculate_delta(previous_value, last_value, divisor)

        return delta


def get_metric(
    title: str,
    mount_df: pd.DataFrame,
    metric_label: str,
    delta_df: pd.DataFrame,
    divisor: int,
):
    """
    Generate a Streamlit metric with a title, a value, and a delta.

    Parameters
    ----------
    title : str
        The title of the metric.
    mount_df : pandas.DataFrame
        The DataFrame containing the value of the metric.
    metric_label : str
        The label to display after the metric value.
    delta_df : pandas.DataFrame
        The DataFrame containing the delta value of the metric.
    divisor : int
        The divisor to apply to the metric value.

    Returns
    -------
    A Streamlit metric.

    """

    return st.metric(
        label=title,
        value=f"{round(mount_df/divisor,2)} {metric_label}",
        delta=f"{delta_df} %" if delta_df is not None else None,
    )


def get_top(
    filtered_df: pd.DataFrame, group_column: str, mount_column: str, top_n: int
):
    """
    Filters the top N entries from a DataFrame based on a specified column.

    Args:
        filtered_df (pd.DataFrame): The DataFrame to filter and sort.
        group_column (str): The column to group the DataFrame by.
        mount_column (str): The column whose values are to be summed and sorted.
        top_n (int): The number of top entries to return.

    Returns:
        pd.DataFrame: A DataFrame containing the top 5 entries with the highest sums in the specified column.
    """

    df = (
        filtered_df.groupby(group_column, as_index=False)[mount_column]
        .sum()
        .sort_values(by=mount_column, ascending=False)
        .head(top_n)
    )
    return df


def format_top_dataframe(
    df: pd.DataFrame,
    subject_column: str,
    mount_column: str,
    subject_label: str,
    mount_label: str,
    is_mount_format: bool = True,
):
    """
    Formats a DataFrame for display in a Streamlit dataframe widget.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to format.
    subject_column : str
        The column name to display as the subject.
    mount_column : str
        The column name to display as the mount.
    subject_label : str
        The label to use for the subject column.
    mount_label : str
        The label to use for the mount column.
    is_mount_format : bool, optional
        Whether to format the mount column as currency (True) or as a number (False).

    Returns
    -------
    A Streamlit dataframe widget with the formatted DataFrame.
    """

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


def get_circular_graph(df: pd.DataFrame, mount_column: str, subject_column: str):
    """
    Displays a circular graph of the top 5 entries of a DataFrame.

    The graph shows the top 5 entries with the highest sums in the specified column.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to display.
    mount_column : str
        The column name to display as the mount.
    subject_column : str
        The column name to display as the subject.

    Returns
    -------
    A Streamlit figure widget with the circular graph.
    """

    fig, ax = plt.subplots()
    ax.pie(df[mount_column], labels=df[subject_column], autopct="%1.1f%%")
    st.pyplot(fig)


def get_data(database_number: int, year: int, month: int = None):
    # Gets all sales in the system
    sales_array = fetch_dashboard_data("sales", database_number)

    if not sales_array.empty:
        has_sales = True
        if month is None:
            title_header_sales = f"Ventas del año {year}"
            # Filters rows where the year matches
            sales_array_filtered = sales_array[sales_array["year_concept"] == year]
            total_sales = sales_array_filtered["total_sales"].sum()
            average_sales = sales_array_filtered["total_sales"].mean()
            median_sales = sales_array_filtered["total_sales"].median()
            max_sales = sales_array_filtered["total_sales"].max()
            min_sales = sales_array_filtered["total_sales"].min()
            number_of_sales = sales_array_filtered["total_sales"].count()
            number_of_clients = sales_array_filtered["name"].nunique()
        else:
            title_header_sales = f"Ventas del mes del año {year}"
            # Filters rows where the month and year match
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
            number_of_clients = sales_array_filtered["name"].nunique()

    else:  # If there is no data, display a warning message
        st.warning("No hay datos de ventas disponibles")
        has_sales = False

    # Gets all system purchases
    purchases_array = fetch_dashboard_data("purchases", database_number)
    if not purchases_array.empty:
        has_purchases = True
        if month is None:
            title_header_purchases = f"Compras del año {year}"
            # Filters rows where the year matches
            purchases_array_filtered = purchases_array[
                purchases_array["year_concept"] == year
            ]
            total_purchases = purchases_array_filtered["total_purchases"].sum()
            average_purchases = purchases_array_filtered["total_purchases"].mean()
            median_purchases = purchases_array_filtered["total_purchases"].median()
            max_purchases = purchases_array_filtered["total_purchases"].max()
            min_purchases = purchases_array_filtered["total_purchases"].min()
            number_of_purchases = purchases_array_filtered["total_purchases"].count()
            number_of_providers = purchases_array_filtered["name"].nunique()

        else:
            title_header_purchases = f"Compras del mes del año {year}"
            # Filters rows where the month and year match
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
            number_of_providers = purchases_array_filtered["name"].nunique()

    else:  # If there is no data, display a warning message
        has_purchases = False
        st.warning("No hay datos de compras disponibles")

    # Gets all sales per salesperson in the system
    sales_by_seller_array = fetch_dashboard_data("sellers", database_number)
    if not sales_by_seller_array.empty:
        has_sellers = True
        if month is None:
            title_header_seller = f"Ventas del año {year}"
            # Filters rows where the year matches
            sales_by_seller_array_filtered = sales_by_seller_array[
                sales_by_seller_array["year_concept"] == year
            ]
            total_sales_by_seller = sales_by_seller_array_filtered["total_sales"].sum()
            number_of_sellers = sales_by_seller_array_filtered["name"].nunique()

        else:
            title_header_seller = f"Ventas del mes del año {year}"
            # Filters rows where the month and year match
            sales_by_seller_array_filtered = sales_by_seller_array[
                (sales_by_seller_array["month_concept"] == month)
                & (sales_by_seller_array["year_concept"] == year)
            ]
            total_sales_by_seller = sales_by_seller_array_filtered["total_sales"].sum()
            number_of_sellers = sales_by_seller_array_filtered["name"].nunique()

    else:  # If there is no data, display a warning message
        has_sellers = False
        st.warning("No hay datos de ventas por vendedor disponibles")

    # Gets all sales by product in the system
    sales_by_product_array = fetch_dashboard_data("products", database_number)
    if not sales_by_product_array.empty:
        has_products = True
        if month is None:
            title_header_products = f"Volumen de Ventas del año {year}"
            # Filters rows where the year matches
            sales_by_product_array_filtered = sales_by_product_array[
                sales_by_product_array["year_concept"] == year
            ]
            total_qty_by_product = sales_by_product_array_filtered["total_qty"].sum()
        else:
            title_header_products = f"Volumen de Ventas del mes del año {year}"
            # Filters rows where the month and year match
            sales_by_product_array_filtered = sales_by_product_array[
                (sales_by_product_array["month_concept"] == month)
                & (sales_by_product_array["year_concept"] == year)
            ]
            total_qty_by_product = sales_by_product_array_filtered["total_qty"].sum()

    else:  # If there is no data, display a warning message
        has_products = False
        st.warning("No hay datos de ventas por producto disponibles")

    # Get the gross profit margin
    gross_profit_margin_array = fetch_dashboard_data(
        "gross-profit-margin", database_number
    )
    if not gross_profit_margin_array.empty:
        has_profit_margin = True
        if month is None:
            title_header_gpm = f"Margen de Ganancia Bruta del año {year}"
            # Filters rows where the year matches
            gross_profit_margin_array_filtered = gross_profit_margin_array[
                gross_profit_margin_array["year_concept"] == year
            ]
            total_gpm = gross_profit_margin_array_filtered["total_gpm"].sum()
        else:
            title_header_gpm = f"Volumen de Ventas del mes del año {year}"
            # Filters rows where the month and year match
            gross_profit_margin_array_filtered = gross_profit_margin_array[
                (gross_profit_margin_array["month_concept"] == month)
                & (gross_profit_margin_array["year_concept"] == year)
            ]
            total_gpm = gross_profit_margin_array_filtered["total_gpm"].sum()

    else:  # If there is no data, display a warning message
        has_profit_margin = False
        st.warning("No hay datos para calcular el margen de ganancia bruta disponibles")

    # Gets all purchases by product in the system
    purchases_by_product_array = fetch_dashboard_data("goods", database_number)
    if not purchases_by_product_array.empty:
        has_goods = True
        if month is None:
            title_header_goods = f"Volumen de Compras del año {year}"
            # Filters rows where the year matches
            purchases_by_product_array_filtered = purchases_by_product_array[
                purchases_by_product_array["year_concept"] == year
            ]
            total_purchases_qty_by_product = purchases_by_product_array_filtered[
                "total_qty"
            ].sum()
        else:
            title_header_goods = f"Volumen de Compras del mes del año {year}"
            # Filters rows where the month and year match
            purchases_by_product_array_filtered = purchases_by_product_array[
                (purchases_by_product_array["month_concept"] == month)
                & (purchases_by_product_array["year_concept"] == year)
            ]
            total_purchases_qty_by_product = purchases_by_product_array_filtered[
                "total_qty"
            ].sum()

    else:  # If there is no data, display a warning message
        has_goods = False
        st.warning("No hay datos de compras por producto disponibles")

    # Gets all sales and profits in the system
    sales_vs_profits_array = fetch_dashboard_data("sales-vs-profit", database_number)
    if not sales_vs_profits_array.empty:
        has_sales_vs_profits = True

    else:  # If there is no data, display a warning message
        has_sales_vs_profits = False
        st.warning("No hay datos de ventas y ganancias disponibles")

    # Return the data as a dictionary
    return {
        "has_sales": has_sales,
        "title_header_sales": title_header_sales,
        "total_sales": total_sales,
        "average_sales": average_sales,
        "median_sales": median_sales,
        "max_sales": max_sales,
        "min_sales": min_sales,
        "number_of_sales": number_of_sales,
        "has_purchases": has_purchases,
        "title_header_purchases": title_header_purchases,
        "total_purchases": total_purchases,
        "average_purchases": average_purchases,
        "median_purchases": median_purchases,
        "max_purchases": max_purchases,
        "min_purchases": min_purchases,
        "number_of_purchases": number_of_purchases,
        "has_sellers": has_sellers,
        "title_header_seller": title_header_seller,
        "total_sales_by_seller": total_sales_by_seller,
        "has_products": has_products,
        "title_header_products": title_header_products,
        "total_qty_by_product": total_qty_by_product,
        "has_profit_margin": has_profit_margin,
        "title_header_gpm": title_header_gpm,
        "total_gpm": total_gpm,
        "sales_array": sales_array,
        "purchases_array": purchases_array,
        "sales_by_seller_array": sales_by_seller_array,
        "sales_by_product_array": sales_by_product_array,
        "gross_profit_margin_array": gross_profit_margin_array,
        "sales_array_filtered": sales_array_filtered,
        "purchases_array_filtered": purchases_array_filtered,
        "sales_by_seller_array_filtered": sales_by_seller_array_filtered,
        "sales_by_product_array_filtered": sales_by_product_array_filtered,
        "gross_profit_margin_array_filtered": gross_profit_margin_array_filtered,
        "number_of_clients": number_of_clients,
        "number_of_providers": number_of_providers,
        "number_of_sellers": number_of_sellers,
        "has_goods": has_goods,
        "title_header_goods": title_header_goods,
        "total_purchases_qty_by_product": total_purchases_qty_by_product,
        "purchases_by_product_array": purchases_by_product_array,
        "sales_vs_profits_array": sales_vs_profits_array,
        "has_sales_vs_profits": has_sales_vs_profits,
    }


def plot_sales_vs_profits(data):
    """
    Genera una gráfica de líneas con marcas para ventas y ganancias mensuales,
    con formato 'K' y símbolo de moneda en el tooltip.

    Args:
        data (pd.DataFrame): DataFrame con columnas:
            - month_concept
            - year_concept
            - total_sales
            - total_gpm
    """
    # Ordenar por mes para garantizar la secuencia
    data = data.sort_values("month_concept")

    # Agregar nombres de los meses
    data["month_name"] = data["month_concept"].apply(
        lambda x: [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ][x - 1]
    )

    # Cambiar formato para graficar ambas métricas en una sola columna
    melted_data = data.melt(
        id_vars=["month_name"],
        value_vars=["total_sales", "total_gpm"],
        var_name="Métrica",
        value_name="Valor",
    )

    # Mapear nombres descriptivos para las métricas
    metric_labels = {"total_sales": "Ventas", "total_gpm": "Ganancias"}
    melted_data["Métrica"] = melted_data["Métrica"].map(metric_labels)

    # Formato de miles (K) y símbolo de moneda
    melted_data["Valor_formateado"] = melted_data["Valor"].apply(
        lambda x: f"${x/1000:,.1f}K"
    )

    # Crear la gráfica con Altair
    chart = (
        alt.Chart(melted_data)
        .mark_line(point=True)
        .encode(
            x=alt.X("month_name", title="Mes"),
            y=alt.Y("Valor", title="Valor (en pesos)"),
            color=alt.Color(
                "Métrica",
                title="Métrica",
                scale=alt.Scale(
                    domain=["Ventas", "Ganancias"], range=["blue", "green"]
                ),
            ),
            tooltip=[
                alt.Tooltip("month_name", title="Mes"),
                alt.Tooltip("Métrica", title="Métrica"),
                alt.Tooltip("Valor_formateado", title="Monto"),
            ],
        )
        .properties(width=700, height=400, title="Ventas vs Ganancias Mensuales")
    )

    # Mostrar la gráfica con Streamlit
    st.altair_chart(chart, use_container_width=True)


def create_weekly_stacked_chart(dataframe, filter_current_week=True):
    """
    Crea un gráfico de barras apiladas para mostrar ventas y ganancias por semana.

    Args:
        dataframe (pd.DataFrame): DataFrame con las columnas `movement_date`, `sales` y `profit`.
        filter_current_week (bool): Si es True, filtra para mostrar solo la semana actual.

    Returns:
        alt.Chart: Gráfico de Altair.
    """
    # Asegurar que movement_date es datetime
    if not pd.api.types.is_datetime64_any_dtype(dataframe["movement_date"]):
        dataframe["movement_date"] = pd.to_datetime(
            dataframe["movement_date"], errors="coerce"
        )

    # Verificar si hay valores no convertibles
    if dataframe["movement_date"].isnull().any():
        raise ValueError(
            "La columna 'movement_date' contiene valores no válidos para fechas."
        )

    # Obtener la fecha actual y el número de semana actual
    today = pd.Timestamp.now()
    current_week = today.isocalendar().week

    # Agregar columna con el nombre del día de la semana
    dataframe["day_name"] = dataframe["movement_date"].dt.day_name(locale="es_ES")

    # Filtrar la semana en curso si se requiere
    if filter_current_week:
        dataframe["week"] = dataframe["movement_date"].dt.isocalendar().week
        dataframe = dataframe[dataframe["week"] == current_week]
        # Calcular el rango de fechas de la semana actual
        week_start = today - pd.Timedelta(days=today.weekday())
        week_end = week_start + pd.Timedelta(days=6)
    else:
        # Calcular el rango de fechas completo
        week_start = dataframe["movement_date"].min()
        week_end = dataframe["movement_date"].max()

    # Verificar si hay datos en el rango seleccionado
    if dataframe.empty:
        raise ValueError("No hay datos disponibles para el rango seleccionado.")

    # Crear el título dinámico con el rango de fechas
    title = f"Semana del {week_start.strftime('%d/%m/%Y')} al {week_end.strftime('%d/%m/%Y')}"

    # Agrupar por día de la semana
    daily_data = dataframe.groupby("day_name")[["sales", "profit"]].sum().reset_index()

    # Traducir las columnas
    daily_data = daily_data.rename(columns={"sales": "Ventas", "profit": "Ganancias"})

    # Dividir valores en miles para simplificar
    daily_data["Ventas"] /= 1000
    daily_data["Ganancias"] /= 1000

    # Transformar datos al formato largo (long format)
    long_format = daily_data.melt(
        id_vars=["day_name"], var_name="tipo", value_name="monto"
    )

    # Crear el gráfico
    chart = (
        alt.Chart(long_format)
        .mark_bar()
        .encode(
            x=alt.X(
                "day_name:N",
                title="Día de la Semana",
                sort=[
                    "lunes",
                    "martes",
                    "miércoles",
                    "jueves",
                    "viernes",
                    "sábado",
                    "domingo",
                ],
            ),
            y=alt.Y("monto:Q", title="Cantidad (en miles de pesos)"),
            color=alt.Color(
                "tipo:N",
                title="Tipo de Movimiento",
                scale=alt.Scale(
                    domain=["Ventas", "Ganancias"], range=["#1f77b4", "#ff7f0e"]
                ),
            ),
            tooltip=[
                alt.Tooltip("tipo:N", title="Tipo"),
                alt.Tooltip("monto:Q", title="Monto (K)", format=",.1f"),
            ],
        )
        .properties(
            title=alt.TitleParams(
                text=title,  # Título dinámico
                fontSize=16,
                anchor="start",
            ),
            width=700,
            height=400,
        )
    )
    return chart

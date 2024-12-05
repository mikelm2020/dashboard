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


# Convert local image to base64
def image_to_base64(image_path: str) -> str:
    """
    Reads an image file and converts it to a base64 encoded string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """

    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")


def render_header(company_name: str, user_name: str, logo_base64: str):
    """
    Renders a header at the top of the page with the company name and the user name.

    Args:
        company_name (str): The name of the company.
        user_name (str): The name of the user.
        logo_base64 (str): The URL of the logo image.
    """
    # Header container
    with st.container():
        # Apply styles to the entire container
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
@st.cache_data(ttl=3600, show_spinner="Obteniendo datos de API")
def fetch_dashboard_data(endpoint: str, db_number: int) -> pd.DataFrame:
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


def calculate_delta(previous_value: float, last_value: float, divisor: int) -> float:
    """
    Calculates the percentage difference between two values.

    Args:
        previous_value (float): The value of the previous period.
        last_value (float): The value of the current period.
        divisor (int): A divisor to apply to both values, e.g. 1000 to get thousands.

    Returns:
        float: The percentage difference between the two values, rounded to 2 decimal places.
    """

    return (
        round(
            (
                (round(last_value / divisor, 2) - round(previous_value / divisor, 2))
                / round(previous_value / divisor, 2)
            )
            * 100,
            2,
        )
        if previous_value != 0
        else 0
    )


def get_delta(
    number_month: int,
    number_year: int,
    concept_array: pd.DataFrame,
    mount_column: str,
    last_value: float,
    divisor: int,
    delta_type: str,
) -> float:
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
) -> pd.DataFrame:
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


def get_top_multiple_agg(
    filtered_df: pd.DataFrame,
    group_column: str,
    mount_column: str,
    aggregate_column_one: str,
    aggregate_column_two: str,
    top_n: int,
) -> pd.DataFrame:
    """
    Filters the top N entries from a DataFrame based on a specified column and 2 aggregates more.

    Args:
        filtered_df (pd.DataFrame): The DataFrame to filter and sort.
        group_column (str): The column to group the DataFrame by.
        mount_column (str): The column whose values are to be summed and sorted.
        aggregate_column_one (str): Aggregate mumber one column name.
        aggregate_column_two (str): Aggregate number two column name.
        top_n (int): The number of top entries to return.

    Returns:
        pd.DataFrame: A DataFrame containing the top 5 entries with the highest sums in the specified column.
    """

    df = (
        filtered_df.groupby(group_column, as_index=False)
        .agg(
            {
                mount_column: "sum",
                aggregate_column_one: "sum",
                aggregate_column_two: "sum",
            }
        )
        .reset_index()
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


def replace_hyphens_with_underscores(text: str) -> str:
    """
    Replaces all hyphens ('-') in a string with underscores ('_').

    Args:
        text (str): The input string.

    Returns:
        str: The modified string with hyphens replaced by underscores.
    """
    return text.replace("-", "_")


def calculate_metrics(data: pd.DataFrame, column: str) -> dict:
    """
    Calculates key metrics for a given column in the DataFrame.

    Args:
        data (pd.DataFrame): The DataFrame containing the data.
        column (str): The name of the column to calculate metrics for.

    Returns:
        dict: A dictionary containing the calculated metrics.
    """
    return {
        "total": data[column].sum(),
        "average": data[column].mean(),
        "median": data[column].median(),
        "max": data[column].max(),
        "min": data[column].min(),
        "count": data[column].count(),
        "unique": data["name"].nunique() if "name" in data else 0,
    }


def filter_data(data: pd.DataFrame, year: int, month: int = None) -> pd.DataFrame:
    """
    Filters data by year and optionally by month.

    Args:
        data (pd.DataFrame): The DataFrame to filter.
        year (int): The year to filter by.
        month (int): The month to filter by (optional).

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    if month is not None:
        return data[(data["year_concept"] == year) & (data["month_concept"] == month)]
    return data[data["year_concept"] == year]


def process_data(
    endpoint: str, db_number: int, year: int, month: int, column: str, title: str
) -> dict:
    """
    Fetches, filters, calculates metrics, and returns data for a specific endpoint.

    Args:
        endpoint (str): The name of the endpoint.
        db_number (int): The number of the database.
        year (int): The year to filter by.
        month (int): The month to filter by (optional).
        column (str): The name of the column to calculate metrics for.
        title (str): The title of the data.

    Returns:
        dict: A dictionary containing the processed data.
    """
    data = fetch_dashboard_data(endpoint, db_number)
    if data.empty:
        st.warning(f"No hay datos disponibles para {title}")
        return {
            "has_data": False,
            "title": title,
            f"{replace_hyphens_with_underscores(endpoint)}_array": pd.DataFrame(),
            f"{replace_hyphens_with_underscores(endpoint)}_array_filtered": pd.DataFrame(),
        }

    filtered_data = filter_data(data, year, month)
    metrics = calculate_metrics(filtered_data, column)
    metrics.update(
        {
            "has_data": True,
            "title": title,
            f"{replace_hyphens_with_underscores(endpoint)}_array": data,
            f"{replace_hyphens_with_underscores(endpoint)}_array_filtered": filtered_data,
        }
    )
    return metrics


def get_data(database_number: int, year: int, month: int = None) -> dict:
    """
    Fetches and processes dashboard data.

    Args:
        database_number (int): The number of the database.
        year (int): The year to filter by.
        month (int): The month to filter by (optional).

    Returns:
        dict: A dictionary containing the processed data.
    """
    endpoints = {
        "sales": ("sales", "total_sales", "Ventas"),
        "purchases": ("purchases", "total_purchases", "Compras"),
        "sellers": ("sellers", "total_sales", "Ventas por vendedor"),
        "products": ("products", "total_qty", "Ventas por producto"),
        replace_hyphens_with_underscores("gross-profit-margin"): (
            "gross-profit-margin",
            "total_gpm",
            "Margen de Ganancia Bruta",
        ),
        "goods": ("goods", "total_qty", "Compras por producto"),
        replace_hyphens_with_underscores("sales-by-towns"): (
            "sales-by-towns",
            "total_sales",
            "Ventas por Municipio",
        ),
        replace_hyphens_with_underscores("sales-by-lines"): (
            "sales-by-lines",
            "sales",
            "Ventas por Línea",
        ),
        replace_hyphens_with_underscores("sales-by-products"): (
            "sales-by-products",
            "sales",
            "Ventas y Ganancias por Producto",
        ),
        replace_hyphens_with_underscores("sales-by-clients"): (
            "sales-by-clients",
            "sales",
            "Ventas y Ganancias por cliente",
        ),
        replace_hyphens_with_underscores("sales-and-profits-by-towns"): (
            "sales-and-profits-by-towns",
            "sales",
            "Ventas y Ganancias por Municipio",
        ),
        replace_hyphens_with_underscores("sales-and-profits-by-sellers"): (
            "sales-and-profits-by-sellers",
            "sales",
            "Ventas y Ganancias por Vendedor",
        ),
    }

    results = {}
    for key, (endpoint, column, title_prefix) in endpoints.items():
        title = (
            f"{title_prefix} del año {year}"
            if month is None
            else f"{title_prefix} del mes {month} del año {year}"
        )
        results[key] = process_data(
            endpoint, database_number, year, month, column, title
        )

    # Combine results into a single dictionary
    return results


def plot_sales_vs_profits(data: pd.DataFrame) -> None:
    """
    Generates a line graph with ticks for monthly sales and profits,
    with 'K' format and currency symbol in the tooltip.

    Args:
        data (pd.DataFrame): DataFrame with columns:
            - month_concept
            - year_concept
            - total_sales
            - total_gpm
    """
    # Sort by month to ensure sequence
    data = data.sort_values("month_concept")

    # Add month names
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

    # Change format to graph both metrics in a single column
    melted_data = data.melt(
        id_vars=["month_name"],
        value_vars=["total_sales", "total_gpm"],
        var_name="Métrica",
        value_name="Valor",
    )

    # Map friendly names to metrics
    metric_labels = {"total_sales": "Ventas", "total_gpm": "Ganancias"}
    melted_data["Métrica"] = melted_data["Métrica"].map(metric_labels)

    # Thousands (K) format and currency symbol
    melted_data["Valor_formateado"] = melted_data["Valor"].apply(
        lambda x: f"${x/1000:,.1f}K"
    )

    # Create the graph with Altair
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

    # Show the graph with Streamlit
    st.altair_chart(chart, use_container_width=True)


def create_weekly_stacked_chart(
    dataframe: pd.DataFrame, filter_current_week: bool = True
):
    """
    Create a stacked bar chart to show sales and profits by week.

    Args:
        dataframe (pd.DataFrame): DataFrame with columns `movement_date`, `sales` and `profit`.
        filter_current_week (bool): If True, filters to show only the current week.

    Returns:
        alt.Chart or str: Altair chart or message if no data available.
    """
    # Ensure movement_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(dataframe["movement_date"]):
        dataframe["movement_date"] = pd.to_datetime(
            dataframe["movement_date"], errors="coerce"
        )

    # Check for non-convertible securities
    if dataframe["movement_date"].isnull().any():
        raise ValueError(
            "La columna 'movement_date' contiene valores no válidos para fechas."
        )

    # Get current date, week number and current year
    today = pd.Timestamp.now()
    current_week = today.isocalendar().week
    current_year = today.isocalendar().year

    # Add column with the name of the day of the week
    dataframe["day_name"] = dataframe["movement_date"].dt.day_name(locale="es_ES")

    # Filter by week and current year if required
    if filter_current_week:
        dataframe["week"] = dataframe["movement_date"].dt.isocalendar().week
        dataframe["year"] = dataframe["movement_date"].dt.isocalendar().year

        # Filter by current year and current week
        dataframe = dataframe[
            (dataframe["week"] == current_week) & (dataframe["year"] == current_year)
        ]

        # Calculate the date range of the current week
        week_start = today - pd.Timedelta(days=today.weekday())
        week_end = week_start + pd.Timedelta(days=6)
    else:
        # Calculate full date range
        week_start = dataframe["movement_date"].min()
        week_end = dataframe["movement_date"].max()

    # Check if there is data in the selected range
    if dataframe.empty:
        # Return an empty message or graphic
        return "No hay datos disponibles para el rango seleccionado."

    # Create dynamic title with date range
    title = f"Semana del {week_start.strftime('%d/%m/%Y')} al {week_end.strftime('%d/%m/%Y')}"

    # Group by day of the week
    daily_data = dataframe.groupby("day_name")[["sales", "profit"]].sum().reset_index()

    # Translate the columns
    daily_data = daily_data.rename(columns={"sales": "Ventas", "profit": "Ganancias"})

    # Divide values ​​into thousands for simplicity
    daily_data["Ventas"] /= 1000
    daily_data["Ganancias"] /= 1000

    # Transform data to long format
    long_format = daily_data.melt(
        id_vars=["day_name"], var_name="tipo", value_name="monto"
    )

    # Create the chart
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
                text=title,  # dynamic title
                fontSize=16,
                anchor="start",
            ),
            width=700,
            height=400,
        )
    )
    return chart


def generate_donut_chart(
    dataframe: pd.DataFrame,
    name_title: str,
    tooltip_name_title: str,
    column_total_amount: str,
    is_graphing_amounts=True,
):
    """
    Generate a donut graph with Altair for the top.
    Includes manual formatting for the weight and percentage symbol.

    Args:
        dataframe (pd.DataFrame): DataFrame with columns 'name' and 'total_sales'.
        name_title str: title for the element name of the top.
        tooltip_name_title str: title for the tooltip of element name of the top.
        column_total_amount str: name of the amouunt field
        is_graphing_amounts bool: Are amounts being graphed?
    """
    if dataframe.empty:
        st.warning(f"No hay datos para mostrar en el top de {name_title}.")
        return

    if not {"name", column_total_amount}.issubset(dataframe.columns):
        st.error(
            f"El DataFrame no contiene las columnas requeridas: 'name', '{column_total_amount}'."
        )
        return

    if not pd.api.types.is_numeric_dtype(dataframe[column_total_amount]):
        st.error(f"La columna '{column_total_amount}' debe contener valores numéricos.")
        return

    # Calculate the percentage
    dataframe = dataframe.copy()
    total_sales_sum = dataframe[column_total_amount].sum()
    if total_sales_sum == 0:
        st.warning("Las ventas totales son cero. No se puede generar la gráfica.")
        return

    dataframe["percentage"] = (dataframe[column_total_amount] / total_sales_sum) * 100

    # Format values ​​for the tooltip
    if is_graphing_amounts:
        dataframe["formatted_sales"] = dataframe[column_total_amount].apply(
            lambda x: f"${x:,.2f}"
        )
    else:
        dataframe["formatted_sales"] = dataframe[column_total_amount].apply(
            lambda x: f"{x:,.1f}"
        )

    dataframe["formatted_percentage"] = dataframe["percentage"].apply(
        lambda x: f"{x:.1f}%"
    )

    # Create the donut graph
    chart = (
        alt.Chart(dataframe)
        .mark_arc(innerRadius=50, outerRadius=100)
        .encode(
            theta=alt.Theta(
                field=column_total_amount, type="quantitative", title="Ventas Totales"
            ),
            color=alt.Color(field="name", type="nominal", title=name_title),
            tooltip=[
                alt.Tooltip("name:N", title=tooltip_name_title),
                alt.Tooltip("formatted_sales:N", title="Ventas"),
                alt.Tooltip("formatted_percentage:N", title="Porcentaje"),
            ],
        )
        .properties(width=400, height=400, title=f"Top de {name_title} (Dona)")
    )

    # Render the graph in Streamlit
    st.altair_chart(chart, use_container_width=True)


def create_table(
    dataframe: pd.DataFrame,
    column_map: dict,
    column_amount_one: str = "sales",
    column_amount_two: str = "profit",
    title_one: str = "Venta",
    title_two: str = "Ganancia",
):
    """
    Create an interactive table with custom filters and headers.

    Args:
        dataframe (pd.DataFrame): DataFrame with original data.
        column_map (dict): Dictionary that maps original column names to custom names.
        column_amount_one (str): Name of the sales or purchases column.
        column_amount_two (str): Name of the profit or expense column.
        title_one (str): Title for the sales or purchases column.
        title_two (str): Title for the profit or expense column.
    """

    # Divide amounts by 1000 and add "K" to the format
    dataframe[column_amount_one] = dataframe[column_amount_one] / 1000
    dataframe[column_amount_two] = dataframe[column_amount_two] / 1000

    # Select dictionary columns and rename for display
    displayed_df = dataframe[list(column_map.keys())]
    displayed_df.columns = [column_map[col] for col in displayed_df.columns]

    # Show index from 1
    displayed_df = displayed_df.reset_index(drop=True)
    displayed_df.index = displayed_df.index + 1

    # Show table with styles
    st.dataframe(
        displayed_df.style.set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", "#FFDDC1"),
                        ("color", "black"),
                        ("font-weight", "bold"),
                    ],
                }
            ]
        ).format(
            {
                title_one: "${:,.2f}K",
                title_two: "${:,.2f}K",
                "Cantidad": "{:,.1f}",
            }  # Format for specific columns
        ),
        use_container_width=True,
    )

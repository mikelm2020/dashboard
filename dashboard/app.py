import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from dotenv import load_dotenv
from streamlit_authenticator.utilities import LoginError
from yaml.loader import SafeLoader

load_dotenv()

# Loading config file
with open("../config.yaml", "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)

initial_year = int(os.getenv("INITIAL_YEAR"))
final_year = datetime.now().year
number_of_databases = int(os.getenv("NUMBER_OF_DATABASES"))
number_of_entries = int(os.getenv("TOP_N"))


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


st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
    initial_sidebar_state="auto",
)

# Creating the authenticator object
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)


if st.session_state["authentication_status"]:
    # database number, Month and year filters
    database_number = st.sidebar.selectbox(
        "Seleccione el número de empresa", list(range(1, number_of_databases + 1))
    )
    year = st.sidebar.selectbox(
        "Seleccione el año", list(range(initial_year, final_year + 1))
    )
    month = st.sidebar.selectbox("Seleccione el mes", ["Todos"] + list(range(1, 13)))
    if month == "Todos":
        month = None

    company_environment = f"COMPANY_NAME_{database_number}"
    name_of_company = os.getenv(company_environment)

    st.write("___")
    authenticator.logout()
    company_section, name_section = st.columns(2)
    with company_section:
        st.write(f"DASHBOARD: {name_of_company}")
    with name_section:
        st.write(f"Bienvenido: *{st.session_state['name']}*")
    st.write("___")

    # FastAPI Base URL
    base_url = os.getenv("BASE_URL")

    # Gets all sales in the system
    sales_array = fetch_dashboard_data("sales", database_number)

    if not sales_array.empty:
        has_sales = True
        if month is None:
            title_header = f"Ventas del año {year}"
            # Filters rows where the year matches
            sales_array_filtered = sales_array[sales_array["year_concept"] == year]
            total_sales = sales_array_filtered["total_sales"].sum()
            average_sales = sales_array_filtered["total_sales"].mean()
            median_sales = sales_array_filtered["total_sales"].median()
            max_sales = sales_array_filtered["total_sales"].max()
            min_sales = sales_array_filtered["total_sales"].min()
            number_of_sales = sales_array_filtered["total_sales"].count()
        else:
            title_header = f"Ventas del mes del año {year}"
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
        else:
            title_header_seller = f"Ventas del mes del año {year}"
            # Filters rows where the month and year match
            sales_by_seller_array_filtered = sales_by_seller_array[
                (sales_by_seller_array["month_concept"] == month)
                & (sales_by_seller_array["year_concept"] == year)
            ]
            total_sales_by_seller = sales_by_seller_array_filtered["total_sales"].sum()

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

    # Saving config file
    with open("../config.yaml", "w", encoding="utf-8") as file:
        yaml.dump(config, file, default_flow_style=False)

    # Create tabs
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
        # Calculate sales metrics
        if has_sales:
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
                get_metric(
                    "Ventas Promedio", average_sales, "mdp", delta_average_sales, 1000
                )

            col3, col4 = st.columns(2)
            with col3:
                get_metric(
                    "Mediana Ventas", median_sales, "mdp", delta_median_sales, 1000
                )
            with col4:
                get_metric("Maxima Venta", max_sales, "mdp", delta_max_sales, 1000)

            col5, col6 = st.columns(2)
            with col5:
                get_metric("Minima Venta", min_sales, "mdp", delta_min_sales, 1000)
            with col6:
                get_metric(
                    "Volumen de ventas",
                    number_of_sales,
                    "facturas",
                    delta_number_of_sales,
                    1,
                )
        else:
            st.warning("No hay datos de ventas disponibles")

        # Calculate purchasing metrics
        if has_purchases:
            delta_purchases = None
            delta_average_purchases = None
            delta_median_purchases = None
            delta_max_purchases = None
            delta_min_purchases = None
            delta_number_of_purchases = None
            purchases_array_filtered_previous = None

            delta_purchases = get_delta(
                month,
                year,
                purchases_array,
                "total_purchases",
                total_purchases,
                1000,
                "sum",
            )

            delta_average_purchases = get_delta(
                month,
                year,
                purchases_array,
                "total_purchases",
                average_purchases,
                1000,
                "mean",
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
                month,
                year,
                purchases_array,
                "total_purchases",
                max_purchases,
                1000,
                "max",
            )

            delta_min_purchases = get_delta(
                month,
                year,
                purchases_array,
                "total_purchases",
                min_purchases,
                1000,
                "min",
            )

            delta_number_of_purchases = get_delta(
                month,
                year,
                purchases_array,
                "total_purchases",
                number_of_purchases,
                1,
                "count",
            )

            col7, col8 = st.columns(2)
            with col7:
                get_metric("Compras", total_purchases, "mdp", delta_purchases, 1000)
            with col8:
                get_metric(
                    "Compras Promedio",
                    average_purchases,
                    "mdp",
                    delta_average_purchases,
                    1000,
                )

            col9, col10 = st.columns(2)
            with col9:
                get_metric(
                    "Mediana Compras",
                    median_purchases,
                    "mdp",
                    delta_median_purchases,
                    1000,
                )
            with col10:
                get_metric(
                    "Maxima Compra", max_purchases, "mdp", delta_max_purchases, 1000
                )

            col11, col12 = st.columns(2)
            with col11:
                get_metric(
                    "Minima Compra", min_purchases, "mdp", delta_min_purchases, 1000
                )
            with col12:
                get_metric(
                    "Volumen de Compras",
                    number_of_purchases,
                    "compras",
                    delta_number_of_purchases,
                    1,
                )

            # Calculate metrics
            delta_gross_profit_margin = None
            sales_array_filtered_previous = None

            delta_gross_profit_margin = get_delta(
                month,
                year,
                gross_profit_margin_array,
                "total_gpm",
                total_gpm,
                1000,
                "sum",
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
        else:
            st.warning("No hay datos de compras disponibles")

    with tab2:
        if has_sales:
            # Get total sales
            if total_sales is not None:
                st.header(f"{title_header}: $ {total_sales:,.2f}")
            else:
                st.warning("No hay datos de ventas disponibles")

            st.header(f"Los {number_of_entries} primeros mejores clientes")
            # Show Top N Clients
            top_clients = get_top(
                sales_array_filtered, "name", "total_sales", number_of_entries
            )

            left_section, right_section = st.columns([0.7, 0.3])
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
        else:
            st.warning("No hay datos de ventas disponibles")

    with tab3:
        if has_purchases:
            # Get total purchases
            if total_purchases is not None:
                st.header(f"{title_header_purchases}: $ {total_purchases:,.2f}")
            else:
                st.warning("No hay datos de ventas disponibles")

            st.header(f"Los {number_of_entries} primeros mejores proveedores")
            # Show Top N Suppliers
            top_providers = get_top(
                purchases_array_filtered, "name", "total_purchases", number_of_entries
            )

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
        else:
            st.warning("No hay datos de compras disponibles")

    with tab4:
        if has_sellers:
            # Get total sales by seller
            if total_sales_by_seller is not None:
                st.header(f"{title_header_seller}: $ {total_sales_by_seller:,.2f}")
            else:
                st.warning("No hay datos de ventas disponibles")

            st.header(f"Los {number_of_entries} primeros mejores vendedores")
            # Show Top N Sellers
            top_sellers = get_top(
                sales_by_seller_array_filtered, "name", "total_sales", number_of_entries
            )

            left_section, right_section = st.columns([0.7, 0.3])
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
        else:
            st.warning("No hay datos de ventas por vendedor disponibles")

    with tab5:
        if has_products:
            # Get total sales by product
            if total_qty_by_product is not None:
                st.header(f"{title_header_products}:  {total_qty_by_product:,.0f}")
            else:
                st.warning("No hay datos de ventas disponibles")

            st.header(f"Los {number_of_entries} primeros mejores productos")
            # Show Top N Products
            top_products = get_top(
                sales_by_product_array_filtered, "name", "total_qty", number_of_entries
            )

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
        else:
            st.warning("No hay datos de ventas por producto disponibles")

elif st.session_state["authentication_status"] is False:
    st.error("Username/password son incorrectos")
elif st.session_state["authentication_status"] is None:
    st.warning("Por favor ingrese username y password")

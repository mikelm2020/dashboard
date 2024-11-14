import os
from datetime import datetime

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
    }

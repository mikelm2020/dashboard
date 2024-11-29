import os
from datetime import datetime

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import streamlit as st
import utilities
from dotenv import load_dotenv
from streamlit_extras.metric_cards import style_metric_cards

load_dotenv()


initial_year = int(os.getenv("INITIAL_YEAR"))
final_year = datetime.now().year
number_of_databases = int(os.getenv("NUMBER_OF_DATABASES"))
number_of_entries = int(os.getenv("TOP_N"))

# database number, Month and year filters
database_number = st.session_state["database_number_select"]
year = st.session_state["year_select"]
month = st.session_state["month_select"]
if month == "Todos":
    month = None

company_environment = f"COMPANY_NAME_{database_number}"
name_of_company = os.getenv(company_environment)

logo = os.getenv("LOGO")
logo_path = f"./{logo}"
logo_base64 = utilities.image_to_base64(logo_path)


# Get haeder
utilities.render_header(name_of_company, st.session_state["name"], logo_base64)

# Get data from database
data = utilities.get_data(database_number, year, month)

with st.container():
    st.markdown("<hr>", unsafe_allow_html=True)

# Get metrics
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if data["has_sales"]:
            delta_average_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["average_sales"],
                1000,
                "mean",
            )
            utilities.get_metric(
                ":material/sell: Ventas Promedio",
                data["average_sales"],
                "K",
                delta_average_sales,
                1000,
            )
    with col2:
        if data["has_sales"]:
            delta_median_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["median_sales"],
                1000,
                "median",
            )
            utilities.get_metric(
                ":material/sell: Mediana Ventas",
                data["median_sales"],
                "K",
                delta_median_sales,
                1000,
            )
    with col3:
        if data["has_sales"]:
            delta_max_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["max_sales"],
                1000,
                "max",
            )
            utilities.get_metric(
                ":material/sell: Maxima Venta",
                data["max_sales"],
                "K",
                delta_max_sales,
                1000,
            )
    with col4:
        if data["has_sales"]:
            delta_min_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["min_sales"],
                1000,
                "min",
            )
            utilities.get_metric(
                ":material/sell: Minima Venta",
                data["min_sales"],
                "K",
                delta_min_sales,
                1000,
            )
    style_metric_cards("#00")

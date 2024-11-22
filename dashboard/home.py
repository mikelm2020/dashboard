import os
from datetime import datetime

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import streamlit as st
import utilities
from dotenv import load_dotenv
from streamlit_extras.grid import grid
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
            delta_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["total_sales"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/sell: Total Ventas",
                data["total_sales"],
                "K",
                delta_sales,
                1000,
            )
    with col2:
        if data["has_profit_margin"]:
            delta_gross_profit_margin = None
            gross_profit_margin_array_filtered_previous = None

            delta_gross_profit_margin = utilities.get_delta(
                month,
                year,
                data["gross_profit_margin_array"],
                "total_gpm",
                data["total_gpm"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/attach_money: Total Ganancias",
                data["total_gpm"],
                "K",
                delta_gross_profit_margin,
                1000,
            )
    with col3:
        if data["has_products"]:
            delta_products = None
            sales_by_product_array_filtered_previous = None

            delta_products = utilities.get_delta(
                month,
                year,
                data["sales_by_product_array"],
                "total_qty",
                data["total_qty_by_product"],
                1,
                "sum",
            )
            utilities.get_metric(
                ":material/shopping_bag: Total Productos",
                data["total_qty_by_product"],
                "",
                delta_products,
                1,
            )
    with col4:
        if data["has_sales"]:
            delta_clients = None

            delta_clients = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "total_sales",
                data["number_of_clients"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/group: Total Clientes",
                data["number_of_clients"],
                "",
                delta_clients,
                1,
            )

style_metric_cards("#00")


def home():
    my_grid = grid(4, [2, 1], [1, 2], [2, 1], vertical_align="bottom")  # noqa: F841
    # Row 1:

    if data["has_sales"]:
        delta_sales = None

        delta_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["total_sales"],
            1000,
            "sum",
        )
        my_grid.utilities.get_metric(
            "Ingresos Netos", data["total_sales"], "K", delta_sales, 1000
        )

    if data["has_sales"]:
        delta_sales = None

        delta_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["total_sales"],
            1000,
            "sum",
        )
        my_grid.utilities.get_metric(
            "Ingresos Netos", data["total_sales"], "K", delta_sales, 1000
        )

    # my_grid.line_chart(random_df, use_container_width=True)
    # # Row 2:
    # my_grid.selectbox("Select Country", ["Germany", "Italy", "Japan", "USA"])
    # my_grid.text_input("Your name")
    # my_grid.button("Send", use_container_width=True)
    # # Row 3:
    # my_grid.text_area("Your message", height=40)
    # # Row 4:
    # my_grid.button("Example 1", use_container_width=True)
    # my_grid.button("Example 2", use_container_width=True)
    # my_grid.button("Example 3", use_container_width=True)
    # my_grid.button("Example 4", use_container_width=True)
    # # Row 5 (uses the spec from row 1):
    # with my_grid.expander("Show Filters", expanded=True):
    #     st.slider("Filter by Age", 0, 100, 50)
    #     st.slider("Filter by Height", 0.0, 2.0, 1.0)
    #     st.slider("Filter by Weight", 0.0, 100.0, 50.0)
    # my_grid.dataframe(random_df, use_container_width=True)
    style_metric_cards("#00")


# home()

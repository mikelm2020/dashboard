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
                ":material/shopping_bag: Total Productos vendidos",
                data["total_qty_by_product"],
                "",
                delta_products,
                1,
            )
    with col4:
        if data["has_sales"]:
            delta_clients = None
            sales_array_filtered_previous = None

            delta_clients = utilities.get_delta(
                month,
                year,
                data["sales_array"],
                "name",
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

# Other metrics
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if data["has_sellers"]:
            delta_sellers = None
            sales_by_seller_array_filtered_previous = None

            delta_sellers = utilities.get_delta(
                month,
                year,
                data["sales_by_seller_array"],
                "name",
                data["number_of_sellers"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/groups: Total Vendedores",
                data["number_of_sellers"],
                "",
                delta_sellers,
                1,
            )
    with col2:
        if data["has_purchases"]:
            delta_purchases = None
            purchases_array_filtered_previous = None

            delta_purchases = utilities.get_delta(
                month,
                year,
                data["purchases_array"],
                "total_purchases",
                data["total_purchases"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/shopping_cart: Total Compras",
                data["total_purchases"],
                "K",
                delta_purchases,
                1000,
            )
    with col3:
        if data["has_goods"]:
            delta_goods = None
            purchases_by_product_array_filtered_previous = None

            delta_goods = utilities.get_delta(
                month,
                year,
                data["purchases_by_product_array"],
                "total_qty",
                data["total_purchases_qty_by_product"],
                1,
                "sum",
            )
            utilities.get_metric(
                ":material/shop_two: Total Mercancia comprada",
                data["total_purchases_qty_by_product"],
                "",
                delta_goods,
                1,
            )
    with col4:
        if data["has_purchases"]:
            delta_providers = None
            purchases_array_filtered_previous = None

            delta_providers = utilities.get_delta(
                month,
                year,
                data["purchases_array"],
                "name",
                data["number_of_providers"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/partner_exchange: Total Proveedores",
                data["number_of_providers"],
                "",
                delta_providers,
                1,
            )


style_metric_cards("#00")

# Graphs

# Obtener el año actual y el mes actual
current_year = year
current_month = month if month is not None else 12

sales_array_filtered = data["sales_array"][
    ["month_concept", "year_concept", "total_sales"]
]
gross_profit_array_filtered = data["gross_profit_margin_array"][
    ["month_concept", "year_concept", "total_gpm"]
]

# Agrupar y sumar las ventas
sales_grouped = sales_array_filtered.groupby(
    ["year_concept", "month_concept"], as_index=False
).agg({"total_sales": "sum"})

# Agrupar y sumar las ganancias
profits_grouped = gross_profit_array_filtered.groupby(
    ["year_concept", "month_concept"], as_index=False
).agg({"total_gpm": "sum"})

# 3. Filtrar por el año actual y meses hasta el mes actual
sales_filtered = sales_grouped[
    (sales_grouped["year_concept"] == current_year)
    & (sales_grouped["month_concept"] <= current_month)
]

profits_filtered = profits_grouped[
    (profits_grouped["year_concept"] == current_year)
    & (profits_grouped["month_concept"] <= current_month)
]

# Combinar los DataFrames en uno solo
combined_df = pd.merge(
    sales_filtered,
    profits_filtered,
    on=["month_concept", "year_concept"],
    how="inner",
)
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        # Llamar a la función de graficado con el DataFrame combinado
        utilities.plot_sales_vs_profits(combined_df)

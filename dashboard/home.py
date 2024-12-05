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
        if data["sales"]["has_data"]:
            delta_sales = None
            sales_array_filtered_previous = None

            delta_sales = utilities.get_delta(
                month,
                year,
                data["sales"]["sales_array"],
                "total_sales",
                data["sales"]["total"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/sell: Total Ventas",
                data["sales"]["total"],
                "K",
                delta_sales,
                1000,
            )
    with col2:
        if data["gross_profit_margin"]["has_data"]:
            delta_gross_profit_margin = None
            gross_profit_margin_array_filtered_previous = None

            delta_gross_profit_margin = utilities.get_delta(
                month,
                year,
                data["gross_profit_margin"]["gross_profit_margin_array"],
                "total_gpm",
                data["gross_profit_margin"]["total"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/attach_money: Total Ganancias",
                data["gross_profit_margin"]["total"],
                "K",
                delta_gross_profit_margin,
                1000,
            )
    with col3:
        if data["products"]["has_data"]:
            delta_products = None
            sales_by_product_array_filtered_previous = None

            delta_products = utilities.get_delta(
                month,
                year,
                data["products"]["products_array"],
                "total_qty",
                data["products"]["total"],
                1,
                "sum",
            )
            utilities.get_metric(
                ":material/shopping_bag: Total Productos vendidos",
                data["products"]["total"],
                "",
                delta_products,
                1,
            )
    with col4:
        if data["sales_by_clients"]["has_data"]:
            delta_clients = None
            sales_array_filtered_previous = None

            delta_clients = utilities.get_delta(
                month,
                year,
                data["sales_by_clients"]["sales_by_clients_array"],
                "name",
                data["sales_by_clients"]["unique"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/group: Total Clientes",
                data["sales_by_clients"]["unique"],
                "",
                delta_clients,
                1,
            )

# Other metrics
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if data["sellers"]["has_data"]:
            delta_sellers = None
            sales_by_seller_array_filtered_previous = None

            delta_sellers = utilities.get_delta(
                month,
                year,
                data["sellers"]["sellers_array"],
                "name",
                data["sellers"]["unique"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/groups: Total Vendedores",
                data["sellers"]["unique"],
                "",
                delta_sellers,
                1,
            )
    with col2:
        if data["purchases"]["has_data"]:
            delta_purchases = None
            purchases_array_filtered_previous = None

            delta_purchases = utilities.get_delta(
                month,
                year,
                data["purchases"]["purchases_array"],
                "total_purchases",
                data["purchases"]["total"],
                1000,
                "sum",
            )
            utilities.get_metric(
                ":material/shopping_cart: Total Compras",
                data["purchases"]["total"],
                "K",
                delta_purchases,
                1000,
            )
    with col3:
        if data["goods"]["has_data"]:
            delta_goods = None
            purchases_by_product_array_filtered_previous = None

            delta_goods = utilities.get_delta(
                month,
                year,
                data["goods"]["goods_array"],
                "total_qty",
                data["goods"]["total"],
                1,
                "sum",
            )
            utilities.get_metric(
                ":material/shop_two: Total Mercancia comprada",
                data["goods"]["total"],
                "",
                delta_goods,
                1,
            )
    with col4:
        if data["purchases"]["has_data"]:
            delta_providers = None
            purchases_array_filtered_previous = None

            delta_providers = utilities.get_delta(
                month,
                year,
                data["purchases"]["purchases_array"],
                "name",
                data["purchases"]["unique"],
                1,
                "nunique",
            )
            utilities.get_metric(
                ":material/partner_exchange: Total Proveedores",
                data["purchases"]["unique"],
                "",
                delta_providers,
                1,
            )


style_metric_cards("#00")

# Graphs

# Get current year and current month
current_year = year
current_month = month if month is not None else 12

sales_array_filtered = data["sales"]["sales_array"][
    ["month_concept", "year_concept", "total_sales"]
]
gross_profit_array_filtered = data["gross_profit_margin"]["gross_profit_margin_array"][
    ["month_concept", "year_concept", "total_gpm"]
]

# Group and add sales
sales_grouped = sales_array_filtered.groupby(
    ["year_concept", "month_concept"], as_index=False
).agg({"total_sales": "sum"})

# Group and add profits
profits_grouped = gross_profit_array_filtered.groupby(
    ["year_concept", "month_concept"], as_index=False
).agg({"total_gpm": "sum"})

# Filter by current year and months to current month
sales_filtered = sales_grouped[
    (sales_grouped["year_concept"] == current_year)
    & (sales_grouped["month_concept"] <= current_month)
]

profits_filtered = profits_grouped[
    (profits_grouped["year_concept"] == current_year)
    & (profits_grouped["month_concept"] <= current_month)
]

# Combine DataFrames into one
combined_df = pd.merge(
    sales_filtered,
    profits_filtered,
    on=["month_concept", "year_concept"],
    how="inner",
)

sales_vs_profits_array = utilities.fetch_dashboard_data(
    "sales-vs-profit", database_number
)

# data for weekly stacked chart
sales_vs_profits_array["movement_date"] = pd.to_datetime(
    sales_vs_profits_array["movement_date"], errors="coerce"
)
sales_vs_profits_array = sales_vs_profits_array.dropna(
    subset=["movement_date"]
)  # Remove rows with invalid dates

chart = utilities.create_weekly_stacked_chart(sales_vs_profits_array)

with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        # Call the graph function with the combined DataFrame
        utilities.plot_sales_vs_profits(combined_df)
    with col2:
        # Call the function and display the graph
        if isinstance(chart, str):  # If the function returned a message
            st.warning(chart)  # Displays the message as a warning
        else:
            st.altair_chart(chart, use_container_width=True)  # Render the graph

with st.container():
    top_clients_filtered = data["sales"]["sales_array_filtered"][
        ["name", "total_sales"]
    ]
    top_clients = utilities.get_top(
        top_clients_filtered, "name", "total_sales", number_of_entries
    )
    top_towns_filtered = data["sales_by_towns"]["sales_by_towns_array_filtered"][
        ["name", "total_sales"]
    ]
    top_towns = utilities.get_top(
        top_towns_filtered, "name", "total_sales", number_of_entries
    )
    col1, col2 = st.columns(2)
    with col1:
        utilities.generate_donut_chart(
            top_clients, "Clientes", "Cliente", "total_sales"
        )
    with col2:
        utilities.generate_donut_chart(
            top_towns, "Municipios", "Municipio", "total_sales"
        )

with st.container():
    col1, col2 = st.columns(2)

    # Obtain Top N Products
    top_products_filtered = data["sales_by_products"][
        "sales_by_products_array_filtered"
    ][["name", "qty"]]
    top_products = utilities.get_top(
        data["sales_by_products"]["sales_by_products_array_filtered"],
        "name",
        "qty",
        number_of_entries,
    )

    top_lines_filtered = data["sales_by_lines"]["sales_by_lines_array_filtered"][
        ["name", "sales"]
    ]
    top_lines = utilities.get_top(
        data["sales_by_lines"]["sales_by_lines_array_filtered"],
        "name",
        "sales",
        number_of_entries,
    )
    with col1:
        utilities.generate_donut_chart(top_lines, "Líneas", "Línea", "sales")
    with col2:
        utilities.generate_donut_chart(
            top_products, "Productos", "Producto", "qty", False
        )

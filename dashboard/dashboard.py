import os
from datetime import datetime

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
    if data["has_sales"]:
        delta_sales = None
        delta_average_sales = None
        delta_median_sales = None
        delta_max_sales = None
        delta_min_sales = None
        delta_number_of_sales = None
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

        delta_average_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["average_sales"],
            1000,
            "mean",
        )

        delta_median_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["median_sales"],
            1000,
            "median",
        )

        delta_max_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["max_sales"],
            1000,
            "max",
        )

        delta_min_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["min_sales"],
            1000,
            "min",
        )

        delta_number_of_sales = utilities.get_delta(
            month,
            year,
            data["sales_array"],
            "total_sales",
            data["number_of_sales"],
            1,
            "count",
        )

        col1, col2 = st.columns(2)
        with col1:
            utilities.get_metric(
                "Ingresos Netos", data["total_sales"], "K", delta_sales, 1000
            )
        with col2:
            utilities.get_metric(
                "Ventas Promedio", data["average_sales"], "K", delta_average_sales, 1000
            )

        col3, col4 = st.columns(2)
        with col3:
            utilities.get_metric(
                "Mediana Ventas", data["median_sales"], "K", delta_median_sales, 1000
            )
        with col4:
            utilities.get_metric(
                "Maxima Venta", data["max_sales"], "K", delta_max_sales, 1000
            )

        col5, col6 = st.columns(2)
        with col5:
            utilities.get_metric(
                "Minima Venta", data["min_sales"], "K", delta_min_sales, 1000
            )
        with col6:
            utilities.get_metric(
                "Volumen de ventas",
                data["number_of_sales"],
                "facturas",
                delta_number_of_sales,
                1,
            )
    else:
        st.warning("No hay datos de ventas disponibles")

    # Calculate purchasing metrics
    if data["has_purchases"]:
        delta_purchases = None
        delta_average_purchases = None
        delta_median_purchases = None
        delta_max_purchases = None
        delta_min_purchases = None
        delta_number_of_purchases = None
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

        delta_average_purchases = utilities.get_delta(
            month,
            year,
            data["purchases_array"],
            "total_purchases",
            data["average_purchases"],
            1000,
            "mean",
        )

        delta_median_purchases = utilities.get_delta(
            month,
            year,
            data["purchases_array"],
            "total_purchases",
            data["median_purchases"],
            1000,
            "median",
        )

        delta_max_purchases = utilities.get_delta(
            month,
            year,
            data["purchases_array"],
            "total_purchases",
            data["max_purchases"],
            1000,
            "max",
        )

        delta_min_purchases = utilities.get_delta(
            month,
            year,
            data["purchases_array"],
            "total_purchases",
            data["min_purchases"],
            1000,
            "min",
        )

        delta_number_of_purchases = utilities.get_delta(
            month,
            year,
            data["purchases_array"],
            "total_purchases",
            data["number_of_purchases"],
            1,
            "count",
        )

        col7, col8 = st.columns(2)
        with col7:
            utilities.get_metric(
                "Compras",
                data["total_purchases"],
                "K",
                delta_purchases,
                1000,
            )
        with col8:
            utilities.get_metric(
                "Compras Promedio",
                data["average_purchases"],
                "K",
                delta_average_purchases,
                1000,
            )

        col9, col10 = st.columns(2)
        with col9:
            utilities.get_metric(
                "Mediana Compras",
                data["median_purchases"],
                "K",
                delta_median_purchases,
                1000,
            )
        with col10:
            utilities.get_metric(
                "Maxima Compra", data["max_purchases"], "K", delta_max_purchases, 1000
            )

        col11, col12 = st.columns(2)
        with col11:
            utilities.get_metric(
                "Minima Compra", data["min_purchases"], "K", delta_min_purchases, 1000
            )
        with col12:
            utilities.get_metric(
                "Volumen de Compras",
                data["number_of_purchases"],
                "compras",
                delta_number_of_purchases,
                1,
            )

        # Calculate metrics
        delta_gross_profit_margin = None
        sales_array_filtered_previous = None

        delta_gross_profit_margin = utilities.get_delta(
            month,
            year,
            data["gross_profit_margin_array"],
            "total_gpm",
            data["total_gpm"],
            1000,
            "sum",
        )

        col13, col14 = st.columns(2)
        with col13:
            utilities.get_metric(
                "Margen de Ganancia Bruta",
                data["total_gpm"],
                "K",
                delta_gross_profit_margin,
                1000,
            )
    else:
        st.warning("No hay datos de compras disponibles")
    style_metric_cards("#00")
with tab2:
    if data["has_sales"]:
        # Get total sales
        if data["total_sales"] is not None:
            st.header(f"{data['title_header_sales']}: $ {data['total_sales']:,.2f}")
        else:
            st.warning("No hay datos de ventas disponibles")

        st.header(f"Los {number_of_entries} primeros mejores clientes")
        # Show Top N Clients
        top_clients = utilities.get_top(
            data["sales_array_filtered"], "name", "total_sales", number_of_entries
        )

        left_section, right_section = st.columns([0.7, 0.3])
        if top_clients.empty:
            st.warning("No hay datos para mostrar")
        else:
            with left_section:
                df_formated = utilities.format_top_dataframe(
                    top_clients, "name", "total_sales", "Cliente", "Ventas"
                )
        with right_section:
            with st.popover("Mostrar gráfica"):
                utilities.get_circular_graph(top_clients, "total_sales", "name")
    else:
        st.warning("No hay datos de ventas disponibles")

with tab3:
    if data["has_purchases"]:
        # Get total purchases
        if data["total_purchases"] is not None:
            st.header(
                f"{data['title_header_purchases']}: $ {data['total_purchases']:,.2f}"
            )
        else:
            st.warning("No hay datos de ventas disponibles")

        st.header(f"Los {number_of_entries} primeros mejores proveedores")
        # Show Top N Suppliers
        top_providers = utilities.get_top(
            data["purchases_array_filtered"],
            "name",
            "total_purchases",
            number_of_entries,
        )

        left_section, right_section = st.columns([0.7, 0.3])
        if top_providers.empty:
            st.warning("No hay datos para mostrar")
        else:
            with left_section:
                df_formated = utilities.format_top_dataframe(
                    top_providers, "name", "total_purchases", "Proveedor", "Compras"
                )
        with right_section:
            with st.popover("Mostrar gráfica"):
                utilities.get_circular_graph(top_providers, "total_purchases", "name")
    else:
        st.warning("No hay datos de compras disponibles")

with tab4:
    if data["has_sellers"]:
        # Get total sales by seller
        if data["total_sales_by_seller"] is not None:
            st.header(
                f"{data['title_header_seller']}: $ {data['total_sales_by_seller']:,.2f}"
            )
        else:
            st.warning("No hay datos de ventas disponibles")

        st.header(f"Los {number_of_entries} primeros mejores vendedores")
        # Show Top N Sellers
        top_sellers = utilities.get_top(
            data["sales_by_seller_array_filtered"],
            "name",
            "total_sales",
            number_of_entries,
        )

        left_section, right_section = st.columns([0.7, 0.3])
        if top_sellers.empty:
            st.warning("No hay datos para mostrar")
        else:
            with left_section:
                df_formated = utilities.format_top_dataframe(
                    top_sellers, "name", "total_sales", "Vendedor", "Ventas"
                )
        with right_section:
            with st.popover("Mostrar gráfica"):
                utilities.get_circular_graph(top_sellers, "total_sales", "name")
    else:
        st.warning("No hay datos de ventas por vendedor disponibles")

with tab5:
    if data["has_products"]:
        # Get total sales by product
        if data["total_qty_by_product"] is not None:
            st.header(
                f"{data['title_header_products']}:  {data['total_qty_by_product']:,.0f}"
            )
        else:
            st.warning("No hay datos de ventas disponibles")

        st.header(f"Los {number_of_entries} primeros mejores productos")
        # Show Top N Products
        top_products = utilities.get_top(
            data["sales_by_product_array_filtered"],
            "name",
            "total_qty",
            number_of_entries,
        )

        left_section, right_section = st.columns([0.7, 0.3])
        if top_products.empty:
            st.warning("No hay datos para mostrar")
        else:
            with left_section:
                df_formated = utilities.format_top_dataframe(
                    top_products, "name", "total_qty", "Producto", "Cantidad", False
                )
        with right_section:
            with st.popover("Mostrar gráfica"):
                utilities.get_circular_graph(top_products, "total_qty", "name")
    else:
        st.warning("No hay datos de ventas por producto disponibles")

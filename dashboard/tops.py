import os
from datetime import datetime

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401
import streamlit as st
import utilities
from dotenv import load_dotenv

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

# Obtener el año actual y el mes actual
current_year = year
current_month = month if month is not None else 12

# Obtain the top lines table
top_lines_filtered = data["sales_by_lines_array_filtered"][
    ["name", "sales", "profit", "qty"]
]
top_lines = utilities.get_top_multiple_agg(
    data["sales_by_lines_array_filtered"],
    "name",
    "sales",
    "profit",
    "qty",
    number_of_entries,
)
column_map = {
    "name": "Línea",
    "sales": "Venta",
    "profit": "Ganancia",
    "qty": "Cantidad",
}

st.header("Top de Líneas")
with st.container():
    utilities.create_table(top_lines, column_map)
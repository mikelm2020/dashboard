import os
from datetime import datetime

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from dotenv import load_dotenv
from streamlit_authenticator.utilities import LoginError
from yaml.loader import SafeLoader

load_dotenv()

config_file = os.getenv("CONFIG_FILE")

initial_year = int(os.getenv("INITIAL_YEAR"))
final_year = datetime.now().year
current_month = datetime.now().month
number_of_databases = int(os.getenv("NUMBER_OF_DATABASES"))
number_of_entries = int(os.getenv("TOP_N"))


# Loading config file
with open(config_file, "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)


st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="auto",
)

# Creating the authenticator object and save in the session state

st.session_state["authenticator"] = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

authenticator = st.session_state["authenticator"]

# Creating a login widget
try:
    authenticator.login()
except LoginError as e:
    st.error(e)


if st.session_state["authentication_status"]:
    user_role = st.session_state["roles"][0]

    with st.sidebar:
        authenticator.logout()

        database_number = st.selectbox(
            "Seleccione el número de empresa",
            list(range(1, number_of_databases + 1)),
            key="database_number_select",
        )
        year = st.selectbox(
            "Seleccione el año",
            list(range(final_year, initial_year - 1, -1)),
            key="year_select",
        )
        month = st.selectbox(
            "Seleccione el mes",
            ["Todos"] + list(range(1, 13)),
            key="month_select",
            index=current_month,
        )
        if month == "Todos":
            month = None

    if user_role == "viewer":
        pages = {
            "Home": [st.Page("home.py", title="Home")],
        }
    elif user_role == "admin":  # For future use
        pages = {
            "Home": [st.Page("home.py", title="Home")],
            "Tops": [st.Page("tops.py", title="Tops")],
            "Estadisicas": [
                st.Page("sales.py", title="Estadisticas de Ventas"),
                st.Page("purchases.py", title="Estaditicas de Compras"),
            ],
        }

        # Contenedor exclusivo para el menú de navegación
        menu_container = st.container()
        with menu_container:
            # Crear el menú de navegación
            pg = st.navigation(pages)
            pg.run()

elif st.session_state["authentication_status"] is False:
    st.error("Username/password son incorrectos")
elif st.session_state["authentication_status"] is None:
    st.warning("Por favor ingrese username y password")


# Saving config file
with open(config_file, "w", encoding="utf-8") as file:
    yaml.dump(config, file, default_flow_style=False)

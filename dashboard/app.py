import os

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from dotenv import load_dotenv
from streamlit_authenticator.utilities import LoginError
from yaml.loader import SafeLoader

load_dotenv()

config_file = os.getenv("CONFIG_FILE")

# Loading config file
with open(config_file, "r", encoding="utf-8") as file:
    config = yaml.load(file, Loader=SafeLoader)


st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="centered",
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

    if user_role == "viewer":
        pages = {
            "Dashboard": [st.Page("dashboard.py", title="Dashboard")],
        }
    elif user_role == "admin":  # For future use
        pages = {
            "Dashboard": [st.Page("dashboard.py", title="Dashboard")],
        }
    pg = st.navigation(pages)
    pg.run()

elif st.session_state["authentication_status"] is False:
    st.error("Username/password son incorrectos")
elif st.session_state["authentication_status"] is None:
    st.warning("Por favor ingrese username y password")


# Saving config file
with open(config_file, "w", encoding="utf-8") as file:
    yaml.dump(config, file, default_flow_style=False)

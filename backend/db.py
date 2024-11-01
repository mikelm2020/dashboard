import os

import firebirdsql  # Driver for Firebird
import pymssql  # Driver for SQL Server
from dotenv import load_dotenv

load_dotenv()


# Función de conexión a SQL Server
def get_db_sqlserver():
    try:
        return pymssql.connect(
            server=os.getenv("DB_SERVER"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
    except pymssql.OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}", flush=True)
        return None


# Función de conexión a Firebird
def connect_to_database():
    host = os.getenv("HOST")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Lee las variables de entono de las bases de datos
    database1_name = os.getenv("FB_1")
    # database2_name = os.getenv("DB_2")
    # database3_name = os.getenv("DB_3")
    path_1 = os.getenv("PATHFB_1")
    # path_2 = os.getenv("PATH_2")
    # path_3 = os.getenv("PATH_3")

    db_path = f"{path_1}{database1_name}"

    # Realizar la conexión a la base de datos seleccionada
    # connection_string = f"DRIVER=Firebird/InterBase(r) driver;SERVER={server_address};DATABASE={selected_db};UID={username};PWD={password}"
    try:
        # conn = pyodbc.connect(connection_string)
        connection = firebirdsql.connect(
            host=host,
            database=db_path,
            user=username,
            password=password,
            charset="UTF8",
        )

        return connection

    except firebirdsql.OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}", flush=True)
        return None


def get_db_connection():
    if os.getenv("DBMS") == "SQLSERVER":
        return get_db_sqlserver()
    elif os.getenv("DBMS") == "FIREBIRD":
        return connect_to_database()

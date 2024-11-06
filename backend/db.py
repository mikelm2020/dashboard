import os

import firebirdsql  # Driver for Firebird
import pymssql  # Driver for SQL Server
from dotenv import load_dotenv

load_dotenv()


# SQL Server connection function
def get_db_sqlserver(db_number: int):
    """
    Connects to a SQL Server database using the pymssql driver.

    If the connection is successful, it returns a pymssql.Connection object.
    If the connection fails, it prints an error message and returns None.

    The connection parameters are expected to be in the environment variables
    DB_SERVER, DB_USER, DB_PASSWORD and DB_NAME.
    """

    db_env_name = f"DB_NAME_{db_number}"

    try:
        return pymssql.connect(
            server=os.getenv("DB_SERVER"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv(db_env_name),
        )
    except pymssql.OperationalError as e:
        print(f"Error al conectar a la base de datos: {e}", flush=True)
        return None


# Firebird connection feature
def connect_to_database(db_number: int):
    """
    Connects to a Firebird database using the firebirdsql driver.

    If the connection is successful, it returns a firebirdsql.Connection object.
    If the connection fails, it prints an error message and returns None.

    The connection parameters are expected to be in the environment variables
    HOST, DB_USER and DB_PASSWORD. The database name is expected to be in the
    environment variable FB_{db_number} and the path to the database file in
    the environment variable PATHFB_{db_number}.
    """

    host = os.getenv("HOST")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database_name = f"FB_{db_number}"
    path = f"PATHFB_{db_number}"

    # Read environment variables from databases
    database_env_name = os.getenv(database_name)
    path_env = os.getenv(path)

    db_path = f"{path_env}{database_env_name}"

    # Make the connection to the selected database
    try:
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


def get_db_connection(db_number: int):
    """
    Connects to a database based on the value of the DBMS environment variable.

    If DBMS is SQLSERVER, it calls get_db_sqlserver().
    If DBMS is FIREBIRD, it calls connect_to_database().

    Returns a connection object if the connection is successful, or None if the connection fails.
    """

    if os.getenv("DBMS") == "SQLSERVER":
        return get_db_sqlserver(db_number)
    elif os.getenv("DBMS") == "FIREBIRD":
        return connect_to_database(db_number)

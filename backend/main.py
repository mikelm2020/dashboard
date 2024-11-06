import os
from typing import List

from db import get_db_connection
from dotenv import load_dotenv
from fastapi import FastAPI
from schemas import (
    GrossProftMarginVector,
    ProductsVector,
    PurchasesVector,
    SalesVector,
    SellersVector,
)

app = FastAPI()

load_dotenv()

if os.getenv("DBMS") == "SQLSERVER":
    year_instruction = ["YEAR(a.FECHA_DOC)", "YEAR(a.FECHA_DOCU)"]
    month_instruction = ["MONTH(a.FECHA_DOC)", "MONTH(a.FECHA_DOCU)"]
    top_instruction = "TOP 5"
elif os.getenv("DBMS") == "FIREBIRD":
    year_instruction = [
        "EXTRACT(YEAR FROM a.FECHA_DOC)",
        "EXTRACT(YEAR FROM a.FECHA_DOCU)",
    ]
    month_instruction = [
        "EXTRACT(MONTH FROM a.FECHA_DOC)",
        "EXTRACT(MONTH FROM a.FECHA_DOCU)",
    ]
    top_instruction = "FIRST 5"


def get_table_name(db_number: int, concept_prefix: str, subject_prefix: str) -> str:
    """
    Constructs table names based on the given database number and prefixes.

    Args:
        db_number (int): The database number to include in the table name.
        concept_prefix (str): The prefix for the concept table name.
        subject_prefix (str): The prefix for the subject table name.

    Returns:
        tuple: A tuple containing the concept table name and the subject table name.
    """

    if len(str(db_number)) >= 1 and len(str(db_number)) <= 9:
        concept_table = f"{concept_prefix}0{db_number}"
        subject_table = f"{subject_prefix}0{db_number}"
    else:
        concept_table = f"{concept_prefix}0{db_number}"
        subject_table = f"{concept_prefix}0{db_number}"
    return concept_table, subject_table


# Endpoint for sales vector
@app.get("/sales/", response_model=List[SalesVector])
def get_sales(db_number: int = 1):
    """
    Endpoint to get sales data from the database.

    Returns a list of SalesVector objects containing the name of the client, the month and year of the sale, and the total sales amount.

    The query is constructed using the instructions for the current database manager system (DBMS).

    If the DBMS is SQLSERVER, the results are returned as a list of dictionaries.

    If the DBMS is FIREBIRD, the results are returned as a list of tuples, which are then converted to a list of dictionaries.
    """

    final_query = ""

    invoices_table, clients_table = get_table_name(db_number, "FACTF", "CLIE")
    query = f"SELECT  b.NOMBRE AS name, {month_instruction[0]} AS month_concept, {year_instruction[0]} AS year_concept,  SUM(a.CAN_TOT) AS total_sales FROM {invoices_table} AS a INNER JOIN {clients_table} AS b ON a.CVE_CLPV = b.CLAVE WHERE (a.STATUS = 'E') AND b.NOMBRE IS NOT NULL"

    final_query = f" GROUP BY b.NOMBRE, {month_instruction[0]}, {year_instruction[0]}"

    query += final_query

    conn = get_db_connection(db_number)
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # We convert each tuple to a dictionary
        formatted_results = [
            {
                "name": row[0],
                "month_concept": row[1],
                "year_concept": row[2],
                "total_sales": row[3],
            }
            for row in results
        ]
        return formatted_results


# Endpoint for shopping vector
@app.get("/purchases/", response_model=List[PurchasesVector])
def get_purchases(db_number: int = 1):
    """
    Endpoint to get purchase data from the database.

    Returns a list of PurchasesVector objects containing the name of the supplier,
    the month and year of the purchase, and the total purchase amount.

    The query is constructed using the instructions for the current database manager system (DBMS).

    If the DBMS is SQLSERVER, the results are returned as a list of dictionaries.

    If the DBMS is FIREBIRD, the results are returned as a list of tuples, which are then converted to a list of dictionaries.
    """

    final_query = ""
    purchases_table, providers_table = get_table_name(db_number, "COMPC", "PROV")
    query = f"SELECT  b.NOMBRE AS name, {month_instruction[0]} AS month_concept, {year_instruction[0]} AS year_concept,  SUM(a.CAN_TOT) AS total_purchases FROM {purchases_table} AS a INNER JOIN {providers_table} AS b ON a.CVE_CLPV = b.CLAVE WHERE (a.STATUS <> 'C') AND b.NOMBRE IS NOT NULL"

    final_query = f" GROUP BY b.NOMBRE, {month_instruction[0]}, {year_instruction[0]}"

    query += final_query

    conn = get_db_connection(db_number)
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # We convert each tuple to a dictionary
        formatted_results = [
            {
                "name": row[0],
                "month_concept": row[1],
                "year_concept": row[2],
                "total_purchases": row[3],
            }
            for row in results
        ]
        return formatted_results


# Endpoint for sales vector by salesperson
@app.get("/sellers/", response_model=List[SellersVector])
def get_sales_of_seller(db_number: int = 1):
    """
    Endpoint to get sales data by salesperson from the database.

    Returns a list of SellersVector objects containing the name of the salesperson, the month and year of the sale, and the total sales amount.

    The query is constructed using the instructions for the current database manager system (DBMS).

    If the DBMS is SQLSERVER, the results are returned as a list of dictionaries.

    If the DBMS is FIREBIRD, the results are returned as a list of tuples, which are then converted to a list of dictionaries.
    """

    final_query = ""
    invoices_table, sellers_table = get_table_name(db_number, "FACTF", "VEND")
    query = f"SELECT  b.NOMBRE AS name, {month_instruction[0]} AS month_concept, {year_instruction[0]} AS year_concept,  SUM(a.CAN_TOT) AS total_sales FROM {invoices_table} AS a INNER JOIN {sellers_table} AS b ON a.CVE_VEND = b.CVE_VEND WHERE (a.STATUS = 'E') AND b.NOMBRE IS NOT NULL"

    final_query = f" GROUP BY b.NOMBRE, {month_instruction[0]}, {year_instruction[0]}"

    query += final_query

    conn = get_db_connection(db_number)
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # We convert each tuple to a dictionary
        formatted_results = [
            {
                "name": row[0],
                "month_concept": row[1],
                "year_concept": row[2],
                "total_sales": row[3],
            }
            for row in results
        ]
        return formatted_results


# Endpoint for sales vector by products
@app.get("/products/", response_model=List[ProductsVector])
def get_sales_of_products(db_number: int = 1):
    """
    Endpoint to get sales data by product from the database.

    Returns a list of ProductsVector objects containing the name of the product, the month and year of the sale, and the total quantity sold.

    The query is constructed using the instructions for the current database manager system (DBMS).

    If the DBMS is SQLSERVER, the results are returned as a list of dictionaries.

    If the DBMS is FIREBIRD, the results are returned as a list of tuples, which are then converted to a list of dictionaries.
    """

    final_query = ""
    movs_table, inventory_table = get_table_name(db_number, "MINVE", "INVE")
    query = f"SELECT  b.DESCR AS name, {month_instruction[1]} AS month_concept, {year_instruction[1]} AS year_concept,  SUM(a.CANT) AS total_qty FROM {movs_table} AS a INNER JOIN {inventory_table} AS b ON a.CVE_ART = b.CVE_ART WHERE (a.TIPO_DOC = 'F') AND b.DESCR IS NOT NULL"

    final_query = f" GROUP BY b.DESCR, {month_instruction[1]}, {year_instruction[1]}"

    query += final_query

    conn = get_db_connection(db_number)
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # We convert each tuple to a dictionary
        formatted_results = [
            {
                "name": row[0],
                "month_concept": row[1],
                "year_concept": row[2],
                "total_qty": row[3],
            }
            for row in results
        ]
        return formatted_results


# Endpoint for gross profit margin
@app.get("/gross-profit-margin/", response_model=List[GrossProftMarginVector])
def get_gross_profit_margin(db_number: int = 1):
    """
    Endpoint to get gross profit margin data from the database.

    Returns a list of GrossProftMarginVector objects containing the month and year of the sale, and the total gross profit margin.

    The query is constructed using the instructions for the current database manager system (DBMS).

    If the DBMS is SQLSERVER, the results are returned as a list of dictionaries.

    If the DBMS is FIREBIRD, the results are returned as a list of tuples, which are then converted to a list of dictionaries.
    """

    final_query = ""
    invoices_table, splits_table = get_table_name(db_number, "FACTF", "PAR_FACTF")
    query = f"SELECT {month_instruction[0]} AS month_concept, {year_instruction[0]} AS year_concept,  SUM(b.CANT * b.PREC) - SUM(b.CANT*b.COST) AS total_gpm FROM {invoices_table} AS a INNER JOIN {splits_table} AS b ON a.CVE_DOC = b.CVE_DOC WHERE (a.STATUS = 'E')"

    final_query = f" GROUP BY {month_instruction[0]}, {year_instruction[0]}"

    query += final_query

    conn = get_db_connection(db_number)
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # We convert each tuple to a dictionary
        formatted_results = [
            {
                "month_concept": row[0],
                "year_concept": row[1],
                "total_gpm": row[2],
            }
            for row in results
        ]
        return formatted_results

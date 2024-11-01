import os
from typing import List, Optional

from db import get_db_connection
from dotenv import load_dotenv
from fastapi import FastAPI
from schemas import Sales, SalesVector, TopItem

app = FastAPI()

load_dotenv()

if os.getenv("DBMS") == "SQLSERVER":
    year_instruction = "YEAR(a.FECHA_DOC)"
    month_instruction = "MONTH(a.FECHA_DOC)"
    top_instruction = "TOP 5"
elif os.getenv("DBMS") == "FIREBIRD":
    year_instruction = "EXTRACT(YEAR FROM a.FECHA_DOC)"
    month_instruction = "EXTRACT(MONTH FROM a.FECHA_DOC)"
    top_instruction = "FIRST 5"


# Endpoint para vector de ventas
@app.get("/sales/", response_model=List[SalesVector])
def get_sales(month: Optional[int] = None, year: Optional[int] = None):
    final_query = ""
    query = f"SELECT  b.NOMBRE AS name, {month_instruction} AS month_concept, {year_instruction} AS year_concept,  SUM(a.CAN_TOT) AS total_sales FROM FACTF01 AS a INNER JOIN CLIE01 AS b ON a.CVE_CLPV = b.CLAVE WHERE (a.STATUS = 'E') AND b.NOMBRE IS NOT NULL"

    final_query = f" GROUP BY b.NOMBRE, {month_instruction}, {year_instruction}"

    query += final_query

    conn = get_db_connection()
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        print(query)

        cursor.execute(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return results
    else:
        # Convertimos cada tupla a un diccionario
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


# Endpoint para total de ventas del año dato escalar
@app.get("/total_sales/", response_model=Sales)
def get_total_sales(month: Optional[int] = None, year: Optional[int] = None):
    query = "SELECT SUM(a.CAN_TOT) AS total FROM FACTF01 AS a WHERE a.STATUS = 'E'"
    if year:
        query += f" AND {year_instruction} = {year}"
    conn = get_db_connection()
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        cursor.execute(query)
        result = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if os.getenv("DBMS") == "SQLSERVER":
        return result
    else:
        return {"total": result[0] if result else 0}


# Endpoint para Top 5 Clientes
@app.get("/top_clients/", response_model=List[TopItem])
def get_top_clients(month: Optional[int] = None, year: Optional[int] = None):
    final_query = ""
    query = f"SELECT {top_instruction} b.NOMBRE AS name, SUM(a.CAN_TOT) AS total FROM FACTF01 AS a INNER JOIN CLIE01 AS b ON a.CVE_CLPV = b.CLAVE WHERE (a.STATUS = 'E') AND b.NOMBRE IS NOT NULL"

    if year:
        query += f" AND {year_instruction} = {year}"
        final_query = f" GROUP BY b.NOMBRE, {year_instruction} ORDER BY total DESC"
    if month:
        query += f" AND {month_instruction} = {month}"
        final_query = f" GROUP BY b.NOMBRE, {month_instruction}, {year_instruction} ORDER BY total DESC"

    query += final_query

    conn = get_db_connection()
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
        # Convertimos cada tupla a un diccionario
        formatted_results = [{"name": row[0], "total": row[1]} for row in results]
        return formatted_results

import os
from typing import List, Optional

from db import get_db_connection
from dotenv import load_dotenv
from fastapi import FastAPI
from schemas import PurchasesVector, SalesVector

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


# Endpoint para vector de compras
@app.get("/purchases/", response_model=List[PurchasesVector])
def get_purchases(month: Optional[int] = None, year: Optional[int] = None):
    final_query = ""
    query = f"SELECT  b.NOMBRE AS name, {month_instruction} AS month_concept, {year_instruction} AS year_concept,  SUM(a.CAN_TOT) AS total_purchases FROM COMPC01 AS a INNER JOIN PROV01 AS b ON a.CVE_CLPV = b.CLAVE WHERE (a.STATUS <> 'C') AND b.NOMBRE IS NOT NULL"

    final_query = f" GROUP BY b.NOMBRE, {month_instruction}, {year_instruction}"

    query += final_query

    conn = get_db_connection()
    cursor = (
        conn.cursor(as_dict=True) if os.getenv("DBMS") == "SQLSERVER" else conn.cursor()
    )
    try:
        # print(query)

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
                "total_purchases": row[3],
            }
            for row in results
        ]
        return formatted_results

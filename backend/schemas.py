from pydantic import BaseModel


class TopItem(BaseModel):
    name: str
    total: float


class SalesVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_sales: float


class Sales(BaseModel):
    total: float


# Modelo de datos para la respuesta de Top de clientes
class TopClient(BaseModel):
    cliente: str
    ventas: float


# Modelo de datos para la respuesta de Top de clientes
class TopProvider(BaseModel):
    proveedor: str
    compras: float


# Modelo de datos para la respuesta de Top de clientes
class TopProductQty(BaseModel):
    producto: str
    ventas_cantidad: float


# Modelo de datos para la respuesta de Top de clientes
class TopProduct(BaseModel):
    producto: str
    ventas: float


# Modelo de datos para la respuesta de Top de clientes
class TopSeller(BaseModel):
    vendedor: str
    ventas: float

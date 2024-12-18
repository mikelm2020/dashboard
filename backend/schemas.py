from datetime import date

from pydantic import BaseModel


class SalesVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_sales: float


class PurchasesVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_purchases: float


class SellersVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_sales: float


class ProductsVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_qty: float


class GrossProftMarginVector(BaseModel):
    month_concept: int
    year_concept: int
    total_gpm: float


class GoodsVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_qty: float


class SalesVsProfitVector(BaseModel):
    movement_date: date
    sales: float
    profit: float


class LinesVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    sales: float
    profit: float
    qty: float


class SalesByProductVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    sales: float
    profit: float
    qty: float


class SalesByClientVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    sales: float
    profit: float
    qty: float


class PurchasesByProviderVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    purchases: float
    spent: float
    qty: float

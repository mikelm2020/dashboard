from pydantic import BaseModel


class SalesVector(BaseModel):
    name: str
    month_concept: int
    year_concept: int
    total_sales: float
